"""Check a frozen task contract against current candidate evidence; never run Aspen.

Exit 0 => DELIVER (final) or CONTINUE (early stage); exit 2 => return RUN.
This is not an automatic scientific/engineering validator.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re
from pathlib import Path
from history_check import his_verdict,decode_history

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def contract_digest(contract):
    return hashlib.sha256(json.dumps(contract,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def nested(data,key):
    for part in key.split('.'):
        data=data[int(part)] if isinstance(data,list) else data[part]
    return data

STAGE_CHECKS = {
    'properties': {key:'review' for key in ('PROP-SOURCES','PROP-ZEROS','PROP-APPLICABILITY','PROP-PHYSICAL','PROP-READBACK')},
    'kinetics': {**{key:'review' for key in ('EARLY-PROPERTIES','KIN-INPUT','KIN-RATES','KIN-LITERATURE','KIN-INDUSTRIAL','KIN-SELECTIVITY')},'KIN-RUN':'history'}
}

def validation_scope(contract,candidate):
    stage=contract.get('validation_stage','final')
    if stage not in ('final','properties','kinetics'):raise ValueError('Unknown validation stage')
    required=contract.get('validation_stages_required',[])
    if not isinstance(required,list) or not all(isinstance(x,str) and x in STAGE_CHECKS for x in required) or len(set(required))!=len(required):
        raise ValueError('Invalid required validation stages')
    if stage=='final' and 'kinetics' in required and 'properties' not in required:
        raise ValueError('Final kinetics audit requires current property audit')
    profile=STAGE_CHECKS.get(stage,{}) if stage!='final' else {'EARLY-'+name.upper():'review' for name in required}
    frozen={item['id']:item for item in contract.get('required_checks',[])}
    for key,kind in profile.items():
        if key not in frozen or frozen[key].get('kind')!=kind:raise ValueError('Missing stage check: '+key)
        if frozen[key].get('allow_na'):raise ValueError('Stage check cannot be waived: '+key)
        if candidate.get('results',{}).get(key,{}).get('status')=='NOT_APPLICABLE':raise ValueError('Stage result cannot be not-applicable: '+key)
    if stage=='kinetics' and not candidate.get('run_id'):raise ValueError('Kinetics requires an actual reactor run')
    return stage

def evaluate(contract,candidate):
    issues=[];verified=[]
    def issue(check_id,reason,owners=None):
        issues.append({'issue_id':'ISSUE-'+check_id,'check_id':check_id,'reason':reason,
                       'owner_modules':owners or ['M15','M09'],
                       'recheck':'New current evidence after repair; recheck all required contract items'})
    if not isinstance(contract,dict) or not isinstance(candidate,dict):
        issue('contract','Task contract and candidate must be objects')
        return {'next_state':'RUN','issues':issues,'return_modules':['M15','M09']}
    stage=contract.get('validation_stage','final')
    try:validation_scope(contract,candidate)
    except (KeyError,TypeError,ValueError,AttributeError) as exc:issue('stage_profile',str(exc))
    if not contract.get('task_id') or candidate.get('task_id')!=contract['task_id']:
        issue('identity','Task identity missing or mismatched')
    if candidate.get('contract_sha256')!=contract_digest(contract):
        issue('contract_revision','Frozen user requirements/check contract changed or hash is missing')
    if not candidate.get('iteration_id'):
        issue('iteration','Current output iteration identity is missing')
    current=candidate.get('current_input',{})
    try:
        if not re.fullmatch(r'[0-9a-fA-F]{64}',current['sha256']):raise ValueError('Invalid input hash')
        if digest(current['path'])!=current['sha256']:raise ValueError('Current input bytes do not match identity')
    except (KeyError,TypeError,ValueError,OSError) as exc:issue('input_identity',str(exc))
    for original in contract.get('original_files',[]):
        try:
            if digest(original['path'])!=original['sha256']:raise ValueError('User original changed')
        except (KeyError,TypeError,ValueError,OSError) as exc:issue('original',str(exc))
    requirements=contract.get('requirements');checks=contract.get('required_checks')
    if not isinstance(requirements,list) or not requirements:
        issue('requirements','Frozen user delivery requirements are missing')
        requirements=[]
    if not isinstance(checks,list) or not checks:
        issue('required_checks','Frozen required check list is missing')
        checks=[]
    results=candidate.get('results',{})
    if not isinstance(results,dict):results={};issue('results','Candidate result map is missing')
    seen=set()
    for spec in requirements+checks:
        if not isinstance(spec,dict) or not isinstance(spec.get('id'),str):
            issue('invalid_spec','Malformed frozen requirement/check');continue
        key=spec['id'];owners=spec.get('owner_modules') or ['M15']
        if not isinstance(owners,list) or not owners or not all(isinstance(m,str) and re.fullmatch(r'M(?:0[1-9]|1[0-5])',m) for m in owners):
            issue(key,'Invalid repair module list');continue
        if key in seen:issue(key,'Duplicate requirement/check id',owners);continue
        seen.add(key)
        if not spec.get('description'):
            issue(key,'Frozen requirement/check description is missing',owners);continue
        kind=spec.get('kind')
        if kind not in ('file','numeric','history','review'):
            issue(key,'Unknown check kind; no implicit pass',owners);continue
        item=results.get(key,{})
        if not isinstance(item,dict):issue(key,'Malformed candidate result',owners);continue
        status=item.get('status','UNVERIFIED')
        if status=='NOT_APPLICABLE':
            if spec.get('allow_na') is True and item.get('reason'):
                verified.append({'id':key,'status':status,'reason':item['reason']});continue
            issue(key,'Not-applicable was not allowed by the frozen task contract',owners);continue
        if status!='PASS':
            issue(key,'Required result is '+str(status),owners);continue
        evidence=item.get('evidence',[])
        if not isinstance(evidence,list) or not evidence:
            issue(key,'PASS without evidence is unverified',owners);continue
        paths=[];valid=True
        for ev in evidence:
            try:
                if not isinstance(ev,dict):raise ValueError('Malformed evidence entry')
                if ev.get('iteration_id')!=candidate['iteration_id']:raise ValueError('Evidence belongs to another output iteration')
                if ev.get('input_sha256')!=current['sha256']:raise ValueError('Evidence belongs to another input revision')
                if ev.get('run_id')!=candidate.get('run_id'):raise ValueError('Evidence belongs to another run')
                path=Path(ev['path'])
                if not path.is_file() or path.stat().st_size==0:raise ValueError('Evidence file is missing or empty')
                if digest(path)!=ev['sha256']:raise ValueError('Evidence bytes changed or hash mismatched')
                paths.append(path)
            except (KeyError,TypeError,ValueError,OSError) as exc:
                issue(key,str(exc),owners);valid=False;break
        if not valid:continue
        try:
            detail={}
            if kind=='file':
                expected=spec.get('extension')
                if expected and not any(p.suffix.lower()==expected.lower() for p in paths):raise ValueError('Requested file extension is missing')
                detail['scope']='File existence/bytes only; opening/editability require a separate review check'
            elif kind=='numeric':
                values=json.loads(paths[0].read_text(encoding='utf-8-sig'))
                value=nested(values,spec['value_key']);target=spec['target']
                if isinstance(value,bool) or isinstance(target,bool) or not isinstance(value,(float,int)) or not isinstance(target,(float,int)):raise ValueError('Numeric value and target must be actual numbers')
                if not math.isfinite(value) or not math.isfinite(target):raise ValueError('Nonfinite numeric evidence')
                if spec.get('unit') is not None and nested(values,spec['unit_key'])!=spec['unit']:raise ValueError('Numeric evidence unit/basis differs from requirement')
                operation=spec['comparison']
                ok={'ge':value>=target,'le':value<=target,'eq':value==target}.get(operation)
                if ok is not True:raise ValueError(f'Numeric requirement not met: actual={value}, comparison={operation}, target={target}')
                detail.update(actual=value,target=target,comparison=operation)
            elif kind=='history':
                if not candidate.get('run_id'):raise ValueError('History check requires a real run identity')
                logs=[p for p in paths if p.suffix.lower()=='.his']
                if len(logs)!=1:raise ValueError('One unambiguous current history is required')
                detail=his_verdict(logs[0].read_bytes())
                reports=[p for p in paths if p.suffix.lower()=='.rep']
                if detail['status']=='UNVERIFIED' and detail['calculation_trace'] and not detail['unclassified_message_lines'] and not any(detail[k] for k in ('severe','errors','warnings')):
                    for report in reports:
                        text,_=decode_history(report.read_bytes())
                        if all(re.search(x,text,re.I) for x in ('Calculations were completed normally','All Unit Operation blocks were completed normally','All streams were flashed normally')):
                            detail.update(status='PASS',basis='Fresh recognized trace plus current normal report completion');break
                if detail['status']!='PASS':raise ValueError('History is '+detail['status']+': '+json.dumps(detail,ensure_ascii=False))
            elif kind=='review':
                if not item.get('method') or not item.get('conclusion'):
                    raise ValueError('Engineering/semantic review requires an actual method and conclusion')
                detail['scope']='Recorded review evidence; script does not certify the review reasoning'
            verified.append({'id':key,'status':'PASS','detail':detail})
        except (KeyError,TypeError,ValueError,OSError,IndexError) as exc:issue(key,str(exc),owners)
    extra=set(results)-seen
    # Additional diagnostic evidence is allowed; it cannot replace a frozen item.
    return {'task_id':contract.get('task_id'),'iteration_id':candidate.get('iteration_id'),
            'run_id':candidate.get('run_id'),'validation_stage':stage,'next_state':'RUN' if issues else ('DELIVER' if stage=='final' else 'CONTINUE'),
            'issues':issues,'return_modules':sorted({m for x in issues for m in x['owner_modules']}),
            'verified':verified,'additional_result_ids':sorted(extra),
            'scope':'Contract/evidence consistency and declared checks, not automatic engineering validity'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract',required=True,type=Path);p.add_argument('--candidate',required=True,type=Path)
    p.add_argument('--report',required=True,type=Path);a=p.parse_args(argv)
    try:result=evaluate(json.loads(a.contract.read_text(encoding='utf-8-sig')),json.loads(a.candidate.read_text(encoding='utf-8-sig')))
    except (ValueError,OSError,TypeError,KeyError,AttributeError) as exc:result={'next_state':'RUN','issues':[{'issue_id':'ISSUE-read','reason':str(exc),'owner_modules':['M09','M15']}],'return_modules':['M09','M15']}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(result['next_state'],a.report)
    return 0 if result['next_state'] in ('DELIVER','CONTINUE') else 2

if __name__=='__main__':raise SystemExit(main())
