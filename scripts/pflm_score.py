"""Explicit offline byte-pattern scoring of a bounded UTF-8 text file."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from horisma_p0.pflm_adapter import load_local_pflm,score_text_bytes
from horisma_p0.operators import ContractError


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('text_file',type=Path)
    parser.add_argument('--model-directory',type=Path,default=Path('.rebuild/models/pflm1'))
    parser.add_argument('--max-bytes',type=int,default=16384)
    args=parser.parse_args()
    try:
        if not 1<=args.max_bytes<=16384:raise ContractError('BYTE_RESOURCE_LIMIT')
        with args.text_file.open('rb') as stream:payload=stream.read(args.max_bytes+1)
        if len(payload)>args.max_bytes:raise ContractError('BYTE_RESOURCE_LIMIT')
        payload.decode('utf-8',errors='strict')
        model=load_local_pflm(args.model_directory)
        result=score_text_bytes(model,payload,max_bytes=args.max_bytes)
        result.pop('bits_per_byte')
        print(json.dumps(result,indent=2))
        return 0
    except (ContractError,OSError,UnicodeError) as exc:
        print(json.dumps({'execution_status':'TERMINAL_FAILURE','error':str(exc)}))
        return 1


if __name__=='__main__':raise SystemExit(main())
