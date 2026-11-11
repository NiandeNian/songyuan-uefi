#!/usr/bin/env python3
"""Extract pinned SM8850 DXE inputs outside Git from public songyuan firmware."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import tempfile
import urllib.request
import zipfile
from uuid import UUID

from uefi_firmware.uefi import FirmwareFile, FirmwareVolume

ROOT = Path(__file__).resolve().parent
URL = ('https://github.com/XiaomiFirmwareUpdaterReleases/firmware_xiaomi_songyuan/releases/download/'
       'stable-25.08.2026/fw_songyuan_songyuan-ota_full-OS3.0.301.0.WGNCNXM-user-16.0-355f85a1fd.zip')
IMAGE_SHA256 = '4817722947551ffda0648d615d83875659281dd5c4deeb6845f4cdf539ac6ea0'


def extract(data, output):
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA256:
        raise ValueError('songyuan uefi.img SHA-256 mismatch')
    if data[:4] != b'\x7fELF' or data[4:6] != b'\x02\x01':
        raise ValueError('expected a little-endian ELF64 UEFI image')
    phoff, = struct.unpack_from('<Q', data, 32)
    stride, count = struct.unpack_from('<HH', data, 54)
    segments = [struct.unpack_from('<IIQQQQQQ', data, phoff + i * stride) for i in range(count)]
    segment, = [p for p in segments if p[0] == 1]
    if segment[3:7] != (0xC6800000, 0xC6800000, 0x2A8000, 0x2A8000):
        raise ValueError('stock UEFI mapping no longer matches the songyuan handoff')
    fv = FirmwareVolume(data[segment[2]:segment[2] + segment[5]])
    if not fv.valid_header or not fv.process():
        raise ValueError('cannot parse the pinned songyuan firmware volume')
    expected = json.loads((ROOT / 'Resources/vendor-inputs.json').read_text())
    found = {}

    def walk(obj):
        if obj is None:
            return
        if isinstance(obj, FirmwareFile):
            names = [s.name for s in obj.sections if s.type == 0x15]
            if names and names[0] in expected:
                name, = names
                if not re.fullmatch(r'[A-Za-z0-9_.+-]+', name):
                    raise ValueError('invalid firmware input name')
                images = [s.data for s in obj.sections if s.type == 0x10]
                raw = [s.data for s in obj.sections if s.type == 0x19]
                payload, = images or raw
                info = expected[name]
                if (len(payload), hashlib.sha256(payload).hexdigest(), str(UUID(bytes_le=obj.guid))) != (info['size'], info['sha256'], info['guid']):
                    raise ValueError('vendor input mismatch: ' + name)
                if name in found:
                    raise ValueError('duplicate vendor input: ' + name)
                found[name] = True
                if images:
                    pe, = struct.unpack_from('<I', payload, 0x3C)
                    if payload[:2] != b'MZ' or payload[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', payload, pe + 4)[0] != 0xAA64:
                        raise ValueError('not an AARCH64 PE image: ' + name)
                    directory = output / name
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / (name + '.efi')).write_bytes(payload)
                    deps = [s.data for s in obj.sections if s.type == 0x13]
                    binary = f'  PE32|{name}.efi|*\n'
                    if deps:
                        dep, = deps
                        if hashlib.sha256(dep).hexdigest() != info['depex_sha256']:
                            raise ValueError('dependency expression mismatch: ' + name)
                        (directory / (name + '.depex')).write_bytes(dep)
                        binary += f'  DXE_DEPEX|{name}.depex|*\n'
                    elif info.get('depex_sha256'):
                        raise ValueError('missing dependency expression: ' + name)
                    (directory / (name + '.inf')).write_text(
                        '[Defines]\n  INF_VERSION = 0x0001001B\n'
                        f'  BASE_NAME = {name}\n  FILE_GUID = {info["guid"]}\n'
                        '  MODULE_TYPE = DXE_DRIVER\n  VERSION_STRING = 1.0\n'
                        '  ENTRY_POINT = EfiEntry\n\n[Binaries.AARCH64]\n' + binary + '\n[Depex]\n  TRUE\n')
                else:
                    directory = output / 'RawFiles'
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / name).write_bytes(payload)
        for child in obj.objects:
            walk(child)
    walk(fv)
    if set(found) != set(expected):
        raise ValueError('missing vendor inputs: ' + ', '.join(set(expected) - set(found)))
    print(f'Verified {len(found)} songyuan vendor inputs from the pinned public UEFI image')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mu-root', type=Path, required=True)
    parser.add_argument('--image', type=Path)
    args = parser.parse_args()
    output = args.mu_root / 'Binaries/songyuan'
    if args.image:
        extract(args.image.read_bytes(), output)
    else:
        with tempfile.TemporaryDirectory(prefix='songyuan-firmware-') as name:
            archive = Path(name) / 'firmware.zip'
            urllib.request.urlretrieve(URL, archive)
            with zipfile.ZipFile(archive) as firmware:
                extract(firmware.read('firmware-update/uefi.img'), output)


if __name__ == '__main__':
    main()
