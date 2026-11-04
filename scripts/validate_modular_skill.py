"""Validate routing graph, content ownership, real local links and Python syntax.

No Aspen calls; this proves skill structure/package properties, not model physics.
"""
import argparse,ast,json,re
from pathlib import Path
from urllib.parse import unquote

def anchors(text):
    ids=set(re.findall(r'<a\s+id=["\']([^"\']+)',text));counts={};fenced=False
    for line in text.splitlines():
        if line.startswith('```'):fenced=not fenced
        if fenced:continue
        m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
        if m:
            label=re.sub(r'<[^>]*>','',m.group(1)).lower()
            label=re.sub(r'[^\w\-\s]','',label).replace(' ','-')
            n=counts.get(label,0);counts[label]=n+1;ids.add(label if n==0 else label+'-'+str(n))
    return ids

def validate(root):
    root=Path(root).resolve();errors=[];warnings=[];links=0;py=0
    registry=json.loads((root/'modules/registry.json').read_text(encoding='utf-8'))
    if registry.get('agents') or registry.get('agent_protocol') or registry.get('memory_protocol'):
        errors.append('Single-session workflow must not contain multi-agent routing')
    if (root/'agents/executor').exists() or (root/'agents/verifier').exists():
        errors.append('Role-specific agent directories must be removed')
    if (root/'scripts/agent_cycle.py').exists():errors.append('Retired agent dispatcher must not be active')
    mods=registry['modules'];expected={f'M{i:02}' for i in range(1,16)}
    if set(mods)!=expected:errors.append('Execution module identities must be M01-M15')
    edges={tuple(x) for x in registry['transitions']}
    required={('INTAKE','PROPERTIES'),('PROPERTIES','PROPERTY_CHECK'),
              ('PROPERTY_CHECK','PROPERTIES'),('PROPERTY_CHECK','RUN'),
              ('RUN','PROPERTIES'),('RUN','OUTPUT'),('OUTPUT','CHECK'),
              ('CHECK','PROPERTIES'),('CHECK','RUN'),('CHECK','DELIVER'),('INTAKE','OUTPUT')}
    if edges!=required:errors.append('Workflow must complete independent property input/check before process simulation')
    guards=registry.get('transition_guards',{})
    if guards.get('PROPERTY_CHECK->RUN')!='P01_CONTINUE_AND_CURRENT_SNAPSHOT_GATE':
        errors.append('Process entry must require current property admission')
    if guards.get('INTAKE->OUTPUT')!='READ_ONLY_NO_EXECUTION_NO_PROPERTY_CHANGES':
        errors.append('Auxiliary route must forbid process execution and property changes')
    if ('RUN','DELIVER') in edges or ('OUTPUT','DELIVER') in edges:errors.append('Direct delivery bypasses output check')
    for key in ('entry','intake','properties','property_check','process_gate','run','output','check'):
        if not (root/registry[key]).is_file():errors.append('Missing lifecycle entry '+key)
    hooks=registry.get('validation_hooks',{})
    if set(hooks)!={'properties','kinetics'}:errors.append('Property and kinetics checks required')
    for stage,hook in hooks.items():
        expected_owner='P00' if stage=='properties' else 'O02'
        if hook.get('owner_module')!=expected_owner or hook.get('owner_agent'):
            errors.append('Wrong stage ownership: '+stage)
        if stage=='properties' and (hook.get('before_process_simulation') is not True or hook.get('failure_route')!='PROPERTIES'):
            errors.append('Property check must precede process execution and return failures to properties')
        if hook.get('event')!=stage+'_entered_or_changed':errors.append('Wrong stage trigger: '+stage)
        if not (root/hook.get('path','')).is_file():errors.append('Missing check module '+stage)
        if hook.get('success_state')!='CONTINUE' or hook.get('failure_state')!='RUN':errors.append('Wrong stage return '+stage)
    for mid,item in mods.items():
        file=root/item['path']
        if not file.is_file():errors.append('Missing module '+mid);continue
        if not item['principles'] or not item['cases']:errors.append('No principles/case layer: '+mid)
        for source in item['principles']:
            if not (root/source).is_file():errors.append('Missing principle source '+source)
        for target in item['related']:
            if target not in mods:errors.append('Unknown linked module '+target)
        seen={mid};todo=[mid]
        while todo:
            v=todo.pop()
            for w in mods.get(v,{}).get('related',[]):
                if w not in seen:seen.add(w);todo.append(w)
        if seen!=expected:errors.append('Module interoperation graph disconnected from '+mid)
    known_cases=set(re.findall(r'\bid=["\'](c\d{2})', (root/'references/principle-case-map.md').read_text(encoding='utf-8')))
    for mid,item in mods.items():
        for case in item['cases']:
            if case.lower() not in known_cases:errors.append('Unknown case '+case+' in '+mid)
    owners=registry.get('resources',{})
    for file in root.rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts or '.git' in file.relative_to(root).parts:continue
        rel=file.relative_to(root).as_posix()
        repo_metadata=rel in {'README.md','NOTICE.md','requirements.txt','.gitattributes','.gitignore'} or rel.startswith('.github/')
        if rel not in owners and not repo_metadata:errors.append('Unowned resource '+rel)
        elif rel in owners and not owners[rel].get('owner'):errors.append('Empty resource owner '+rel)
        if file.suffix=='.py':
            py+=1
            try:ast.parse(file.read_text(encoding='utf-8-sig'),filename=rel)
            except (SyntaxError,UnicodeError) as exc:errors.append(str(exc))
        if file.suffix!='.md':continue
        text=file.read_text(encoding='utf-8-sig')
        for m in re.finditer(r'\[[^\]\n]+\]\(([^)\n]+)\)',text):
            value=m.group(1).strip()
            if '://' in value or value.startswith(('mailto:','<')) or re.match(r'^[A-Za-z]:',value):continue
            dest,sep,anchor=value.partition('#');links+=1
            target=(file.parent/unquote(dest)).resolve() if dest else file
            if not target.is_file():errors.append(f'{rel}: missing {value}')
            elif sep and anchor and target.suffix=='.md' and unquote(anchor) not in anchors(target.read_text(encoding='utf-8-sig')):
                errors.append(f'{rel}: missing anchor {value}')
    case_degree={case:sum(case in m['cases'] for m in mods.values()) for case in {c for m in mods.values() for c in m['cases']}}
    if not any(v>1 for v in case_degree.values()):errors.append('No case is shared across modules')
    return {'status':'PASS' if not errors else 'FAIL','module_count':len(mods),'resource_count':len(owners),'local_links':links,
            'python_syntax_files':py,'workflow':list(map(list,sorted(edges))),'errors':errors,'warnings':warnings,
            'scope':'Routing/references/ownership/syntax only; no Aspen/runtime or scientific validation'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--report',type=Path);a=p.parse_args()
    result=validate(a.root);text=json.dumps(result,ensure_ascii=False,indent=2);print(text)
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(text,encoding='utf-8')
    raise SystemExit(result['status']!='PASS')
