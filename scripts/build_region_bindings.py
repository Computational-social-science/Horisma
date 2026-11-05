"""Compatibility entrypoint delegating to the integrated Horisma research CLI."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from horisma_p0.cli import main as cli_main


def main():
    sys.argv=[sys.argv[0],'--root',str(ROOT),'research-build',*sys.argv[1:]]
    return cli_main()


if __name__=='__main__':
    raise SystemExit(main())
