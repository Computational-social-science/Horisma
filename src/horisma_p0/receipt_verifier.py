"""Verify local receipt bindings; authentic payloads can still contain wrong findings."""
import json
from jsonschema import Draft202012Validator
from .operators import load_json, owned_path, digest
from .automated_review import REQUIRED, decide

RECEIPT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['version', 'producer', 'gate', 'context', 'status', 'artifacts', 'evidence'],
    'properties': {
        'version': {'const': '1.0.0'}, 'producer': {'type': 'string', 'minLength': 1},
        'gate': {'enum': list(REQUIRED)}, 'context': {'type': 'object', 'minProperties': 1},
        'status': {'enum': ['SATISFIED', 'UNRESOLVED', 'REJECTED']},
        'evidence': {'type': 'object', 'required': ['kind'], 'properties': {'kind': {'enum': list(REQUIRED)}}},
        'artifacts': {'type': 'array', 'minItems': 1, 'items': {'type': 'object',
            'additionalProperties': False, 'required': ['path', 'sha256'],
            'properties': {'path': {'type': 'string', 'minLength': 1},
                           'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}}}}}}


def verify_bundle(root, bundle):
    """Missing receipts fail closed; receipts are not cryptographic attestations."""
    context = bundle['context']
    checks = dict.fromkeys(REQUIRED, False)
    errors = {}
    for gate in REQUIRED:
        try:
            binding = bundle['receipts'][gate]
            path = owned_path(root, binding['path'])
            if digest(path.read_bytes()) != binding['sha256']:
                raise ValueError('RECEIPT_DIGEST_MISMATCH')
            receipt = load_json(path)
            if list(Draft202012Validator(RECEIPT_SCHEMA).iter_errors(receipt)):
                raise ValueError('INVALID_TYPED_RECEIPT')
            if receipt['evidence']['kind'] != gate:
                raise ValueError('WRONG_EVIDENCE_TYPE')
            if gate == 'transcription_fidelity' and receipt['evidence'].get('image_status') != 'QUALIFIED_IMAGE_MATCH':
                raise ValueError('UNQUALIFIED_IMAGE_FIDELITY')
            if receipt['gate'] != gate or json.dumps(receipt['context'], sort_keys=True, allow_nan=False) != json.dumps(context, sort_keys=True, allow_nan=False):
                raise ValueError('STALE_OR_WRONG_CONTEXT')
            if receipt['status'] != 'SATISFIED':
                raise ValueError('GATE_UNSATISFIED')
            if not receipt['artifacts']:
                raise ValueError('ARTIFACT_BINDINGS_REQUIRED')
            for artifact in receipt['artifacts']:
                if digest(owned_path(root, artifact['path']).read_bytes()) != artifact['sha256']:
                    raise ValueError('DEPENDENCY_CHANGED')
            checks[gate] = True
        except (KeyError, ValueError, OSError, TypeError) as exc:
            errors[gate] = str(exc)
    return {'checks': checks, 'errors': errors,
            'decision': decide(checks, attempts=bundle.get('attempts', 0)),
            'scope': 'INTEGRITY_AND_CONTEXT_ONLY_NOT_SEMANTIC_AUTHENTICATION'}
