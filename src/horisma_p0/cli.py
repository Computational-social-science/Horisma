"""Explicit, on-demand P0 commands; never starts a background controller."""
import argparse
import json
from pathlib import Path

from .operators import ContractError, acquire_source, index_wikipedia, load_json, save_new_json, validate_ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest='command', required=True)
    acquire = sub.add_parser('acquire')
    acquire.add_argument('source_id')
    acquire.add_argument('url')
    acquire.add_argument('--media', choices=['pdf', 'html'], default='pdf')
    sub.add_parser('index-wikipedia')
    sub.add_parser('validate')
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == 'acquire':
            result = acquire_source(root, args.source_id, args.url, args.media)
        elif args.command == 'index-wikipedia':
            folder = root / 'data/intake/wikipedia/matthew_effect'
            receipt = load_json(folder / 'source_receipt.json')
            result = index_wikipedia((folder / 'page.html').read_bytes(), receipt['sha256'], receipt['revision_id'])
            save_new_json(root / 'data/evidence/p0/matthew-effect-v1/wikipedia_bibliography.json', result)
            result = {'reference_entries': len(result['reference_entries']), 'proposed_work_groups': result['proposed_work_groups'], 'purpose': result['purpose']}
        else:
            result = validate_ledger(root, load_json(root/'data/evidence/p0/matthew-effect-v1/candidate_ledger.v2.json'),
                                     load_json(root/'spec/p0/candidate_ledger.schema.json'), load_json(root/'spec/p0/freeze_manifest.json'))
        print(json.dumps(result, indent=2))
        return 0 if result.get('access_status') != 'WAITING_HUMAN_SOURCE' else 2
    except (ContractError, OSError, ValueError) as exc:
        print(json.dumps({'execution_status': 'TERMINAL_FAILURE', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
