# songyuan-uefi

Mu-Silicium firmware for Redmi K100 Pro Max (`songyuan`, SM8850/Canoe),
adapted from [Typeun/myron-uefi](https://github.com/Typeun/myron-uefi).

The firmware embeds the real UniXNU application, UniXNUDxe boot option registrar
and DarwinBoot loader. It uses the stock framebuffer at `0xfc800000`,
1200 × 2608 pixels with a 4800-byte stride. SMBIOS identifies `songyuan` / `M098FE`.

`Resources/DTBs/songyuan.dtb` was extracted from this phone's captured
`vendor_boot_a.img`, selecting Canoe revision 2 / SoC ID 660. The memory map
validator checks all 48 reserved ranges in this phone's captured live device tree.
The firmware volume remains at `0xa7100000`, size `0x300000`.

## Build

Run the **songyuan UEFI with UniXNU** Actions workflow. It pins Mu-Silicium and
the UniXNU menu/loader source, overlays `Platforms/Xiaomi/songyuanPkg`, and
builds `SILICIUM_UEFI.fd` with the menu and loader inside the firmware volume.

The FD is a firmware volume; the main repository packages it with BootShim into
a raw ARM64 Android header-v4 boot image (text_offset=0, flags=0xa, no ramdisk).
The intended boot method
is `fastboot boot`, without replacing Android boot partitions.

## Validation status

The map has 81 descriptors and 63 AddMem ranges, with all 48 captured live
reservations covered. It uses the measured SM8850 GIC addresses 0x17000000 and
0x17080000, preserves the inherited QSMMUv500 stream/context state, and exposes the framebuffer
through SimpleFbDxe with a write-through framebuffer mapping. SMEM, SHM and
the PDP shared region use uncached mappings. The original SEC/XBL image is
retained at 0xc6800000.

`fetch_vendor_inputs.py` extracts 61 pinned inputs from the public songyuan
OS3.0.301.0.WGNCNXM firmware. The UEFI image, each PE32 and its dependency
expression are checked by SHA-256; the image's ELF load range is checked too.
Inputs are created under Mu-Silicium/Binaries/songyuan outside this source tree.
The old SM8550 aston driver references and OnePlus ACPI table have been replaced.

The native vendor input, framebuffer-cache and CPU-entry builds have now been
temporarily booted on the phone. They remained black, lost USB connectivity and
required a power-key restart. The most recent tested menu image was the SMMU/cache
handoff build, Actions run 43008514330 (SHA-256
`2343c4e8866ca548ec16ead2e2722a7de06043002c48aa6264ee577285db5c5b`).
Android recovered. Its ramoops contents were corrupted Android logs and did not
identify where this UEFI stopped.

SEC no longer clears unrelated SMMU stream/context banks before memory and DXE
initialization. The inherited display/firmware clients keep their translations;
peripheral drivers must quiesce their client before taking over its own domain.
BootShim also completes the FD stores and invalidates instruction cache before
jumping to the copied SEC entry. These corrections address unsafe handoff
operations; successful hardware boot still needs to be established separately.

The [GIC/display UEFI build](https://github.com/NiandeNian/songyuan-uefi/actions/runs/42967547102)
passed for `b155dd5e56c8f4427416f12dd94b190d40743599`, including UniXNU,
UniXNUDxe and DarwinBoot. The
[raw/v4 menu boot.img build](https://github.com/NiandeNian/UniXNU-songyuan/actions/runs/42967976093)
also passed. Actions artifacts expire after 14 days; rebuild this firmware and
pass the new successful run ID to the main repository's menu workflow when needed.

After the SMMU/cache handoff build also remained black, the user authorized
screen probes. `boot_shim.screen_log=true` now adds a general-register-only
framebuffer logger and a temporary stack. It reports entry, CurrentEL/SCTLR,
FDT, firmware copying and the jump to SEC. Early exceptions retain ESR/ELR/FAR
on screen without a reset timer. A DEBUG firmware adds the SEC assembly-entry
marker and the normal Mu-Silicium framebuffer console. Build DEBUG for this
diagnostic test; RELEASE still omits the common firmware debug output.

The first DEBUG FD ran through the SEC cache stages in QEMU, then faulted before
memory initialization. Forty descriptor names had trailing spaces. Mu's exact
`AsciiStriCmp` lookup could not find `Display_Reserved`, and its framebuffer
callers used an uninitialized descriptor. The names are now unpadded and the
validator rejects edge whitespace instead of silently stripping it. The same
correction makes named register/shared-memory regions available to their users.

The name-corrected DEBUG FD reached MMU initialization in QEMU. The next fault
was a scanner read at `0xc6aa8000`, exactly the end of the retained stock FD.
`apply_xbl_bounds.py` now replaces only the hash-checked pinned XBL scanner:
signature lookahead, missing-RET parsing and GUID reads stay inside the retained
region, and ADD address decoding uses the source register. The host guard-page
test rejects the old scanner with SIGSEGV and passes the corrected C code.

[DEBUG run 43013977832](https://github.com/NiandeNian/songyuan-uefi/actions/runs/43013977832)
passed with FD SHA-256
`3e6f30df3b1ce5e6b29912c95c576df3bc2b94916fd38a2dbf55db7d51179447`.
The downloaded FD no longer crosses the retained region in QEMU. It reaches
stock SEC code at `0xc680955c`, which reads through `TPIDR_EL1`; that register is
zero in this static QEMU setup and the read faults at address zero. The setup
does not recreate stock scheduler thread state or SM8850 peripherals. It has
not reached DXE and is not a hardware boot validation. The screen-log and
bounded-scanner firmware builds have not yet been tested on the offline phone.

The 2026-11-11 hardware test of menu run `43015116868` now confirms the
framebuffer stages through `[14] PlatformPeim`. The screen reports a synchronous
exception at stock PC `0xc6808300`. Stock disassembly identifies this as
`ldrb w0, [x20, #0x328]`, with `x20` loaded from `TPIDR_EL1` at `0xc68082d4`,
inside the mutex acquisition used by the scheduler lock service. The photo
does not include FAR or the thread register; a null pointer and an unmapped
retained thread heap cannot yet be distinguished on hardware. Android recovered
with a different boot ID; pstore has no SEC crash record.

DEBUG now retains ESR, FAR and TPIDR on the exception screen, records TPIDR
before/after MMU setup, and marks GUID discovery and every FV InitLock call.
These logs do not alter the stock scheduler or invent thread/HOB contents.
This is a diagnostic build to identify the required runtime mapping or context
repair; the UniXNU menu and iOS boot are still unconfirmed.

The next hardware run (`43025963716`, FD run `43025226578`) confirms
`TPIDR_EL1=0xc6ef02d8` both before and after MMU setup. The first FV InitLock
faults at `0xc6808300`, ESR `0x96000006`, FAR `0xc6ef0600`. FAR is exactly the
live thread plus `0x328`; DFSC 6 means an L2 translation fault. This proves
the thread register survived and the missing runtime map caused this access
to fail. `XBL_Runtime` now reserves/maps the rest of the 16 MiB firmware
envelope (`0xc6aa8000..0xc7800000`) as write-back data. The scanner remains
bounded to the original `0x2a8000` FD, and no thread or scheduler objects are
modified. The envelope conservatively retains adjacent stock runtime data;
its complete original allocation layout is not claimed to have been recovered.
The next temporary hardware boot (`43029794779`, FD run `43028929595`) passed
SEC and reached DXE. The ArmCpuDxe exception screen reports ELR `0xc22e3d84`,
ESR `0x96000007`, FAR `0x01106000`: an L3 translation fault. The captured live
FDT identifies this address as `qcom,ipcc@1106000`, size `0x1000`.
`IPCC` now maps exactly that page as uncached Device MMIO; the existing
`IPC_ROUTER_TOP` range does not cover it. The validator checks its range,
attributes and absence of overlaps. Android recovered after the user held the
power key. This confirms the runtime mapping enabled DXE progress; the new
IPCC mapping and UniXNU menu still require a temporary hardware boot test.

License: BSD-2-Clause-Patent.
