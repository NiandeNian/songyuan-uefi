#!/usr/bin/env python3
"""Validate the songyuan Mu-Silicium memory map before building UEFI.

The map mixes live-FDT reserved ranges with allocations owned by UEFI/XNU.  An
overlap can corrupt still-running Qualcomm firmware before DarwinBoot starts, so
this check is intentionally strict and has no device access.
"""

from __future__ import annotations

import re
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAP = ROOT / "Platforms/Xiaomi/songyuanPkg/Library/MemoryMapLib/MemoryMapLib.c"
ENTRY = re.compile(
    r'\{"(?P<name>[^"]+)",\s*'
    r'(?P<base>0x[0-9A-Fa-f]+),\s*'
    r'(?P<size>0x[0-9A-Fa-f]+),\s*'
    r'(?P<hob>\w+),\s*(?P<resource>\w+),'
)


def fail(message: str) -> None:
    raise SystemExit(f"memory-map: {message}")


text = MAP.read_text(encoding="utf-8")
entries = []
for match in ENTRY.finditer(text):
    item = match.groupdict()
    item["name"] = item["name"].strip()
    item["base"] = int(item["base"], 16)
    item["size"] = int(item["size"], 16)
    entries.append(item)

if len(entries) < 70:
    fail(f"only {len(entries)} descriptors parsed; expected the live-FDT map plus UEFI allocations")

by_name = {entry["name"]: entry for entry in entries}
required = {
    "GUNYAH_HYP_REGION": (0x80000000, 0x00E00000),
    "SPLASH_REGION": (0xFC800000, 0x02B00000),
    "RAMOOPS_REGION": (0xFF400000, 0x00200000),
    "HYPERVISOR_EXTENDED_": (0xC3DD0000, 0x00A30000),
    "TRUST_UI_VM_REGION": (0xF3800000, 0x05000000),
    "OEM_VM_REGION": (0xF8800000, 0x03800000),
    "UEFI_FD": (0xA7100000, 0x00300000),
    "Kernel": (0xA8000000, 0x10000000),
    "XNU_Payload": (0xF0000000, 0x03800000),
    "DXE_Heap": (0xB8000000, 0x0BDD0000),
}
for name, expected in required.items():
    entry = by_name.get(name)
    if entry is None:
        fail(f"missing {name}")
    actual = entry["base"], entry["size"]
    if actual != expected:
        fail(f"{name} is {actual[0]:#x}+{actual[1]:#x}, expected {expected[0]:#x}+{expected[1]:#x}")

if by_name["XNU_Payload"]["base"] + by_name["XNU_Payload"]["size"] != by_name["TRUST_UI_VM_REGION"]["base"]:
    fail("XNU payload no longer ends at the trust-UI reservation boundary")
if by_name["DXE_Heap"]["base"] + by_name["DXE_Heap"]["size"] != by_name["HYPERVISOR_EXTENDED_"]["base"]:
    fail("DXE heap no longer ends at the hypervisor-extended reservation boundary")

# Only AddMem descriptors participate in the physical-memory HOB map.  MMIO
# AddDev/NoHob ranges deliberately occupy a different resource namespace.
memory = sorted(
    (entry for entry in entries if entry["hob"] == "AddMem"),
    key=lambda entry: (entry["base"], entry["size"], entry["name"]),
)
for left, right in zip(memory, memory[1:]):
    left_end = left["base"] + left["size"]
    if left_end > right["base"]:
        fail(
            f'{left["name"]} {left["base"]:#x}..{left_end:#x} overlaps '
            f'{right["name"]} {right["base"]:#x}..{right["base"] + right["size"]:#x}'
        )

hardware = json.loads((ROOT / 'Resources/songyuan-hardware.json').read_text(encoding='utf-8'))
for region in hardware['reserved_memory']:
    base, end = region['base'], region['base'] + region['size']
    covering = [item for item in memory if item['base'] <= base and item['base'] + item['size'] >= end and item['resource'] == 'MEM_RES']
    if not covering:
        fail(f"live reservation {region['name']} {base:#x}..{end:#x} is not reserved in the firmware map")
print(f"PASS: {len(entries)} descriptors, {len(memory)} AddMem ranges, no overlaps; {len(hardware['reserved_memory'])} songyuan live reservations covered")
