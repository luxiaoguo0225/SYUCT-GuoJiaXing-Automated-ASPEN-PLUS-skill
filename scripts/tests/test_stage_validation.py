"""Early checks in a single-session modular workflow, using synthetic evidence."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_delivery import evaluate,contract_digest,STAGE_CHECKS
import test_delivery_loop as fixtures

class StageChecks(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.DeliveryLoop();self.f.setUp();self.addCleanup(self.f.tearDown)
    def stage(self,name,required=None):
        f=self.f;f.contract['validation_stage']=name
        if required is not None:f.contract['validation_stages_required']=required
        profile=STAGE_CHECKS.get(name,{}) if name!='final' else {'EARLY-'+x.upper():'review' for x in (required or [])}
        f.contract['required_checks']=[]
        f.candidate['results']={k:v for k,v in f.candidate['results'].items() if k=='purity'}
        for key,kind in profile.items():
            f.contract['required_checks'].append({'id':key,'kind':kind,'description':'Synthetic evidence fixture','owner_modules':['M01' if name=='properties' else 'M03']})
            f.candidate['results'][key]={'status':'PASS','method':'Direct fixture read; no agent identity','conclusion':'Fixture scope only','evidence':[f.ev(f.log if kind=='history' else f.data)]}
        f.candidate['contract_sha256']=contract_digest(f.contract)
        return f.contract,f.candidate
    def refresh(self):self.f.candidate['contract_sha256']=contract_digest(self.f.contract)
    def test_property_success_only_continues(self):
        self.assertEqual(evaluate(*self.stage('properties'))['next_state'],'CONTINUE')
    def test_zero_issue_returns_to_run(self):
        c,a=self.stage('properties');a['results']['PROP-ZEROS']['status']='FAIL'
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_source_check_cannot_be_omitted(self):
        c,a=self.stage('properties');c['required_checks']=[x for x in c['required_checks'] if x['id']!='PROP-SOURCES'];self.refresh()
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_zero_check_cannot_be_waived(self):
        c,a=self.stage('properties');c['required_checks'][1]['allow_na']=True;self.refresh()
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_missing_physical_evidence_not_pass(self):
        c,a=self.stage('properties');a['results']['PROP-PHYSICAL']['status']='UNVERIFIED'
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_kinetics_requires_actual_run(self):
        c,a=self.stage('kinetics');a['run_id']=None
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_kinetics_needs_valid_properties(self):
        c,a=self.stage('kinetics');a['results']['EARLY-PROPERTIES']['status']='UNVERIFIED'
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_missing_industrial_comparison_not_pass(self):
        c,a=self.stage('kinetics');a['results']['KIN-INDUSTRIAL']['status']='UNVERIFIED'
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_kinetics_success_continues_without_agents(self):
        self.assertEqual(evaluate(*self.stage('kinetics'))['next_state'],'CONTINUE')
    def test_final_needs_stage_audits(self):
        c,a=self.stage('final',['properties','kinetics']);del a['results']['EARLY-KINETICS']
        self.assertEqual(evaluate(c,a)['next_state'],'RUN')
    def test_final_current_evidence_delivers_without_agents(self):
        self.assertEqual(evaluate(*self.stage('final',['properties','kinetics']))['next_state'],'DELIVER')
    def test_final_kinetics_cannot_drop_properties(self):
        self.assertEqual(evaluate(*self.stage('final',['kinetics']))['next_state'],'RUN')
    def test_unknown_stage_not_default_pass(self):
        self.assertEqual(evaluate(*self.stage('unknown'))['next_state'],'RUN')

if __name__=='__main__':unittest.main()
