"""Behavioral regression for failed-output return and fresh-evidence delivery."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_delivery import evaluate,digest,contract_digest

class DeliveryLoop(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=self.root/'input.inp';self.source.write_text('fixed input')
        self.data=self.root/'values.json';self.data.write_text(json.dumps({'purity':{'value':.995,'unit':'mass_fraction'}}))
        self.log=self.root/'case.his';self.log.write_text('SUMMARY OF SIMULATION ERRORS\nSevere Errors 0\nErrors 0\nWarnings 0')
        self.contract={'task_id':'task','requirements':[{'id':'purity','kind':'numeric','description':'Required mass purity','value_key':'purity.value','unit_key':'purity.unit','unit':'mass_fraction','comparison':'ge','target':.99,'owner_modules':['M02']}],
            'required_checks':[{'id':'history','kind':'history','description':'No simulation errors/warnings','owner_modules':['M15','M08']}],
            'original_files':[{'path':str(self.source),'sha256':digest(self.source)}]}
        self.candidate={'task_id':'task','iteration_id':'i1','run_id':'r1','current_input':{'path':str(self.source),'sha256':digest(self.source)},'results':{}}
        self.candidate['contract_sha256']=contract_digest(self.contract)
        for key,path in [('purity',self.data),('history',self.log)]:self.candidate['results'][key]={'status':'PASS','evidence':[self.ev(path)]}
    def tearDown(self):self.temp.cleanup()
    def ev(self,path):return {'path':str(path),'sha256':digest(path),'iteration_id':self.candidate['iteration_id'],'input_sha256':self.candidate['current_input']['sha256'],'run_id':self.candidate['run_id']}
    def test_complete_current_evidence_can_deliver(self):self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'DELIVER')
    def test_below_target_returns_to_process_module(self):
        self.data.write_text(json.dumps({'purity':{'value':.98,'unit':'mass_fraction'}}));self.candidate['results']['purity']['evidence']=[self.ev(self.data)]
        result=evaluate(self.contract,self.candidate);self.assertEqual(result['next_state'],'RUN');self.assertIn('M02',result['return_modules'])
    def test_error_returns_to_diagnostics(self):
        self.log.write_text('** ERROR\nCalculation failed');self.candidate['results']['history']['evidence']=[self.ev(self.log)]
        result=evaluate(self.contract,self.candidate);self.assertEqual(result['next_state'],'RUN');self.assertIn('M15',result['return_modules'])
    def test_missing_frozen_requirement_is_not_satisfied_by_extra_result(self):
        self.candidate['results']['something_else']=self.candidate['results'].pop('purity')
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_old_run_evidence_cannot_pass(self):
        self.candidate['run_id']='r2';self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_changed_file_requires_new_evidence(self):
        self.data.write_text('modified after review');self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_old_input_revision_cannot_pass(self):
        self.candidate['results']['purity']['evidence'][0]['input_sha256']='0'*64
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_not_applicable_cannot_hide_failure(self):
        self.candidate['results']['history']={'status':'NOT_APPLICABLE','reason':'avoid warning'}
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_unknown_history_is_unverified(self):
        self.log.write_text('Run2 returned');self.candidate['results']['history']['evidence']=[self.ev(self.log)]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_unit_mismatch_cannot_pass(self):
        self.data.write_text(json.dumps({'purity':{'value':.995,'unit':'mole_fraction'}}));self.candidate['results']['purity']['evidence']=[self.ev(self.data)]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_user_original_protection(self):
        self.source.write_text('original changed');self.candidate['current_input']['sha256']=digest(self.source)
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_repair_requires_fresh_output_then_passes(self):
        self.log.write_text('* WARNING\nUnresolved');self.candidate['results']['history']['evidence']=[self.ev(self.log)]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
        self.log.write_text('NO ERRORS OR WARNINGS GENERATED');self.candidate['iteration_id']='i2';self.candidate['run_id']='r2'
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
        for key,path in [('purity',self.data),('history',self.log)]:self.candidate['results'][key]['evidence']=[self.ev(path)]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'DELIVER')
    def test_no_empty_contract_pass(self):self.assertEqual(evaluate({'task_id':'task','requirements':[],'required_checks':[]},self.candidate)['next_state'],'RUN')
    def test_review_requires_explanation_and_evidence(self):
        self.contract['required_checks'].append({'id':'physical','kind':'review','description':'Independent physical applicability','owner_modules':['M01']})
        self.candidate['contract_sha256']=contract_digest(self.contract)
        self.candidate['results']['physical']={'status':'PASS','evidence':[self.ev(self.data)]}
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
        self.candidate['results']['physical'].update(method='Independent source comparison documented in evidence',conclusion='Within the declared tested range')
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'DELIVER')
    def test_deleting_original_user_requirement_invalidates_frozen_contract(self):
        self.contract['requirements']=[]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')
    def test_malformed_evidence_returns_problem(self):
        self.candidate['results']['history']['evidence']=[None]
        self.assertEqual(evaluate(self.contract,self.candidate)['next_state'],'RUN')

if __name__=='__main__':unittest.main()
