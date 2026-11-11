"""Replace only the fixed upstream XBL scanner with its bounded variant."""
from pathlib import Path
import argparse, hashlib

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mu-root', type=Path, required=True)
args = parser.parse_args()
path = args.mu_root / 'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/XblProtocols.c'
expected = 'c79d3cef46c60466751f7e79e3b26837fb2a292738dfa58bcaa9fb9084db67fe'
source = path.read_bytes().replace(b'\r\n', b'\n')
if hashlib.sha256(source).hexdigest() != expected:
    raise SystemExit('Pinned Mu XBL source differs; inspect before applying the bounded scanner')
path.write_bytes((Path(__file__).resolve().parent / 'Patches/XblProtocols.c').read_bytes())
print('Applied FD bounds to the pinned XBL protocol scanner')
