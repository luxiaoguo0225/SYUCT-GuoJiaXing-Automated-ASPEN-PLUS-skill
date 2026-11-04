"""Behavioral property admission tests; no Aspen or live UI calls."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_delivery import STAGE_CHECKS, contract_digest, digest
from check_process_gate import evaluate_gate
from aspen_plus_bridge import AspenPlus
import test_delivery_loop as fixtures


class ProcessGate(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.DeliveryLoop()
        self.f.setUp()
        self.addCleanup(self.f.tearDown)
        f=self.f
        self.frozen=f.root/'property_snapshot.json'
        self.current=f.root/'current_readback.json'
        self.settings={'components':['A','B'],'methods':{'global':'NRTL'},
            'scope':{'T_C':[20,100],'P_kPa':[100,110],'phases':['V','L']},
            'parameters':[{'pair':['A','B'],'source_type':'database','source':'native IG bank','Aij':1,'Aji':2}],
            'source_inventory':{'binary_parameters_required':True,
                'user_parameter_count':0,'unresolved_source_count':0,
                'available':['native IG bank','other available bank'],
                'enabled':['native IG bank','other available bank']}}
        self.frozen.write_text(json.dumps(self.settings))
        self.current.write_text(json.dumps(self.settings,indent=2))
        f.contract['validation_stage']='properties'
        f.contract['required_checks']=[{'id':key,'kind':'review','description':'Synthetic property check','owner_modules':['M01']} for key in STAGE_CHECKS['properties']]
        f.candidate['results']={'purity':f.candidate['results']['purity']}
        for key in STAGE_CHECKS['properties']:
            f.candidate['results'][key]={'status':'PASS','method':'Synthetic fixture scope',
                'conclusion':'Fixture, not physical validation','evidence':[f.ev(self.frozen)]}
        f.candidate['contract_sha256']=contract_digest(f.contract)
        f.candidate['property_snapshot']={'path':str(self.frozen),'sha256':digest(self.frozen)}
        self.contract=f.root/'property-contract.json'
        self.candidate=f.root/'property-candidate.json'
        self.request_path=f.root/'gate-request.json'
        self.request={'property_contract':str(self.contract),'property_candidate':str(self.candidate),
                      'current_property_snapshot':str(self.current)}
        self.save()

    def save(self):
        self.contract.write_text(json.dumps(self.f.contract))
        self.candidate.write_text(json.dumps(self.f.candidate))
        self.request_path.write_text(json.dumps(self.request))

    def verdict(self):
        self.save()
        return evaluate_gate(self.request)

    def test_current_passed_property_stage_allows_process(self):
        self.assertEqual(self.verdict()['next_state'],'PROCESS_READY')

    def test_unexplained_zero_cannot_be_overridden_by_good_numeric_result(self):
        self.f.candidate['results']['PROP-ZEROS']['status']='UNVERIFIED'
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_inapplicable_nonzero_record_blocks_process(self):
        self.f.candidate['results']['PROP-APPLICABILITY']['status']='FAIL'
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_missing_stage_file_blocks_process(self):
        self.request['property_contract']=str(self.f.root/'absent.json')
        self.assertFalse(evaluate_gate(self.request)['process_run_allowed'])

    def test_numeric_final_deliver_cannot_replace_property_stage(self):
        self.f.contract['validation_stage']='final'
        self.f.candidate['contract_sha256']=contract_digest(self.f.contract)
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_changed_source_blocks_old_approval(self):
        changed=copy.deepcopy(self.settings)
        changed['parameters'][0]['source']='different bank'
        self.current.write_text(json.dumps(changed))
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_expanded_temperature_envelope_requires_recheck(self):
        changed=copy.deepcopy(self.settings)
        changed['scope']['T_C'][1]=200
        self.current.write_text(json.dumps(changed))
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_relabelled_frozen_snapshot_without_stage_evidence_does_not_pass(self):
        self.frozen.write_text(json.dumps({**self.settings,'methods':{'global':'OTHER'}}))
        self.f.candidate['property_snapshot']['sha256']=digest(self.frozen)
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_snapshot_not_bound_to_every_check_blocks_process(self):
        self.f.candidate['results']['PROP-PHYSICAL']['evidence']=[self.f.ev(self.f.data)]
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_same_snapshot_path_is_not_a_fresh_readback(self):
        self.request['current_property_snapshot']=str(self.frozen)
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_snapshot_with_no_scope_blocks_process(self):
        self.settings.pop('scope')
        for path in (self.frozen,self.current):path.write_text(json.dumps(self.settings))
        self.f.candidate['property_snapshot']['sha256']=digest(self.frozen)
        for key in STAGE_CHECKS['properties']:
            self.f.candidate['results'][key]['evidence']=[self.f.ev(self.frozen)]
        self.assertFalse(self.verdict()['process_run_allowed'])

    def refresh_snapshots(self):
        for path in (self.frozen,self.current):path.write_text(json.dumps(self.settings))
        self.f.candidate['property_snapshot']['sha256']=digest(self.frozen)
        for key in STAGE_CHECKS['properties']:
            self.f.candidate['results'][key]['evidence']=[self.f.ev(self.frozen)]

    def test_partial_source_enablement_blocks_process_even_if_reviews_say_pass(self):
        self.settings['source_inventory']['enabled'].pop()
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_missing_source_inventory_blocks_process(self):
        self.settings.pop('source_inventory')
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_pure_component_model_does_not_require_invented_binary_records(self):
        self.settings['components']=['A']
        self.settings['parameters']=[]
        self.settings['source_inventory']={'binary_parameters_required':False,'reason':'Single pure component',
            'user_parameter_count':0,'unresolved_source_count':0}
        self.refresh_snapshots()
        self.assertTrue(self.verdict()['process_run_allowed'])

    def test_user_source_is_forbidden_even_when_all_reviews_pass(self):
        self.settings['parameters'][0]['source']='USER'
        self.settings['allow_user']=True
        self.refresh_snapshots()
        result=self.verdict()
        self.assertFalse(result['process_run_allowed'])
        self.assertIn('USER',result['reason'])

    def test_manual_and_regressed_source_types_have_no_waiver(self):
        for kind in ['USER','manual','regression','literature']:
            with self.subTest(kind=kind):
                self.settings['parameters'][0]['source_type']=kind
                self.refresh_snapshots()
                self.assertFalse(self.verdict()['process_run_allowed'])

    def test_user_field_cannot_hide_inside_a_database_labelled_pair(self):
        self.settings['parameters'][0]['field_sources']={'AIJ':'native IG bank','AJI':' user '}
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_native_user_literal_cannot_hide_as_field_source(self):
        self.settings['parameters'][0]['field_sources']={'AIJ':'0$1.2'}
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_pure_component_user_override_is_also_forbidden(self):
        self.settings['components']=['A']
        self.settings['parameters']=[{'property':'CP','source_type':'database','source':'USER'}]
        self.settings['source_inventory']={'binary_parameters_required':False,'reason':'Single component',
            'user_parameter_count':0,'unresolved_source_count':0}
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_missing_source_or_missing_source_audit_cannot_pass(self):
        self.settings['parameters'][0].pop('source')
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])
        self.settings['parameters'][0]['source']='native IG bank'
        self.settings['source_inventory'].pop('user_parameter_count')
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_positive_user_override_count_blocks_process(self):
        self.settings['source_inventory']['user_parameter_count']=1
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_unknown_sources_cannot_pass_as_database_only(self):
        self.settings['source_inventory']['unresolved_source_count']=1
        self.refresh_snapshots()
        self.assertFalse(self.verdict()['process_run_allowed'])

    def test_bridge_never_calls_run2_with_user_property_input(self):
        self.settings['parameters'][0]['source']='USER'
        self.refresh_snapshots()
        self.save()
        bridge=self.bridge()
        with self.assertRaises(ValueError):bridge.run(property_gate_request=self.request_path)
        bridge.app.Run2.assert_not_called()

    def bridge(self):
        bridge=AspenPlus.__new__(AspenPlus)
        bridge.app=Mock()
        return bridge

    def test_bridge_refuses_run2_without_property_admission(self):
        bridge=self.bridge()
        with self.assertRaises(ValueError):bridge.run()
        bridge.app.Run2.assert_not_called()

    def test_bridge_refuses_run2_when_property_check_failed(self):
        self.f.candidate['results']['PROP-ZEROS']['status']='FAIL'
        self.save()
        bridge=self.bridge()
        with self.assertRaises(ValueError):bridge.run(property_gate_request=self.request_path)
        bridge.app.Run2.assert_not_called()

    def test_bridge_only_calls_run2_after_current_pass(self):
        bridge=self.bridge()
        bridge.run(property_gate_request=self.request_path)
        bridge.app.Run2.assert_called_once_with(False)


if __name__=='__main__':unittest.main()
