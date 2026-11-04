"""Require a current, evidence-bound property stage before process simulation.

Does not run Aspen or infer scientific validity from file identity.
Exit 0: PROCESS_READY; exit 2: return to the independent property track.
"""
import argparse
import json
from pathlib import Path
from check_delivery import STAGE_CHECKS, digest, evaluate


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def database_source(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Missing native property source: ' + label)
    source = value.strip()
    if 'USER' in source.upper() or source.startswith('0$') or any(
            text in source for text in ('用户输入', '用户自定义', '手工输入')):
        raise ValueError('USER property input is forbidden: ' + label)
    return source


def snapshot(path):
    data = load(path)
    if not isinstance(data, dict):
        raise ValueError('Property snapshot must be an object')
    for key in ('components', 'methods', 'scope'):
        if not data.get(key):
            raise ValueError('Incomplete property snapshot: ' + key)
    if not isinstance(data.get('parameters'), list):
        raise ValueError('Property snapshot requires explicit parameter records')
    inventory = data.get('source_inventory')
    if not isinstance(inventory, dict) or not isinstance(inventory.get('binary_parameters_required'), bool):
        raise ValueError('Snapshot requires explicit binary source inventory/scope')
    for key in ('user_parameter_count', 'unresolved_source_count'):
        if type(inventory.get(key)) is not int or inventory[key] != 0:
            raise ValueError('USER/unknown property sources cannot pass: ' + key + ' must be audited as zero')
    if inventory['binary_parameters_required']:
        available, enabled = inventory.get('available'), inventory.get('enabled')
        for values in (available, enabled):
            if not isinstance(values, list) or not values or not all(isinstance(v, str) and v for v in values) or len(set(values)) != len(values):
                raise ValueError('Incomplete/duplicate binary source inventory')
        if set(available) != set(enabled):
            raise ValueError('All available binary sources must be enabled before selection')
        for source in available:
            database_source(source, 'binary source inventory')
        if not data['parameters']:
            raise ValueError('Required binary parameter records are missing')
    elif not inventory.get('reason'):
        raise ValueError('Explain why binary source selection is not required')
    for index, record in enumerate(data['parameters']):
        if not isinstance(record, dict):
            raise ValueError('Property parameter must be a source-bearing record')
        if str(record.get('source_type', '')).strip().lower() != 'database':
            raise ValueError('Only native database property parameters are allowed; USER/manual/regressed inputs are forbidden')
        source = database_source(record.get('source'), 'parameter ' + str(index))
        fields = record.get('field_sources', {})
        if not isinstance(fields, dict):
            raise ValueError('field_sources must contain native source labels')
        for field, field_source in fields.items():
            actual = database_source(field_source, 'parameter ' + str(index) + '/' + field)
            if 'pair' in record and actual != source:
                raise ValueError('Binary pair must retain one complete native database record')
        if 'pair' in record:
            if not inventory['binary_parameters_required'] or source not in inventory['enabled']:
                raise ValueError('Binary property source is not in the enabled native inventory')
    return data


def evaluate_gate(request):
    try:
        contract = load(request['property_contract'])
        candidate = load(request['property_candidate'])
        if contract.get('validation_stage') != 'properties':
            raise ValueError('A property-stage contract is required; final/numerical delivery is insufficient')
        verdict = evaluate(contract, candidate)
        if verdict['next_state'] != 'CONTINUE':
            return {'next_state': 'PROPERTIES', 'process_run_allowed': False,
                    'reason': 'P01 did not pass', 'property_check': verdict}
        frozen = candidate['property_snapshot']
        frozen_path = Path(frozen['path'])
        if digest(frozen_path) != frozen['sha256']:
            raise ValueError('Frozen property snapshot changed')
        for key in STAGE_CHECKS['properties']:
            refs = candidate['results'][key].get('evidence', [])
            if not any(Path(r['path']).resolve() == frozen_path.resolve() and
                       r['sha256'] == frozen['sha256'] for r in refs):
                raise ValueError('Property snapshot is not bound to check: ' + key)
        current_path = Path(request['current_property_snapshot'])
        if current_path.resolve() == frozen_path.resolve():
            raise ValueError('Current readback must be a separate snapshot file')
        if snapshot(frozen_path) != snapshot(current_path):
            raise ValueError('Current property settings or scope differ; return to P00 and recheck')
        return {'next_state': 'PROCESS_READY', 'process_run_allowed': True,
                'task_id': contract['task_id'], 'property_iteration_id': candidate['iteration_id'],
                'property_input_sha256': candidate['current_input']['sha256'],
                'property_contract_sha256': digest(request['property_contract']),
                'property_candidate_sha256': digest(request['property_candidate']),
                'property_snapshot_sha256': frozen['sha256'],
                'current_snapshot_path': str(current_path),
                'current_snapshot_sha256': digest(current_path),
                'scope': 'Current declared property evidence and snapshot only; not engineering certification'}
    except (KeyError, TypeError, ValueError, OSError, AttributeError) as exc:
        return {'next_state': 'PROPERTIES', 'process_run_allowed': False, 'reason': str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = evaluate_gate(load(args.request))
    except (OSError, ValueError) as exc:
        result = {'next_state': 'PROPERTIES', 'process_run_allowed': False, 'reason': str(exc)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(result['next_state'], args.report)
    return 0 if result['process_run_allowed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
