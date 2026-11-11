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

The map has 79 descriptors and 62 AddMem ranges, with all 48 captured live
reservations covered. It uses the measured SM8850 GIC addresses 0x17000000 and
0x17080000, preserves the display SIDs 0x800/0x801, and exposes the framebuffer
through SimpleFbDxe with a write-through framebuffer mapping. SMEM, SHM and
the PDP shared region use uncached mappings. The original SEC/XBL image is
retained at 0xc6800000.

`fetch_vendor_inputs.py` extracts 61 pinned inputs from the public songyuan
OS3.0.301.0.WGNCNXM firmware. The UEFI image, each PE32 and its dependency
expression are checked by SHA-256; the image's ELF load range is checked too.
Inputs are created under Mu-Silicium/Binaries/songyuan outside this source tree.
The old SM8550 aston driver references and OnePlus ACPI table have been replaced.

The phone is online. The earlier gzip/v0 image and raw/v4 repack returned to
Android; the GIC/display-corrected raw/v4 image remained black and required a
power-key restart. The native vendor input build is not yet physically validated.
CI results are recorded separately from hardware results.

The [GIC/display UEFI build](https://github.com/NiandeNian/songyuan-uefi/actions/runs/42967547102)
passed for `b155dd5e56c8f4427416f12dd94b190d40743599`, including UniXNU,
UniXNUDxe and DarwinBoot. The
[raw/v4 menu boot.img build](https://github.com/NiandeNian/UniXNU-songyuan/actions/runs/42967976093)
also passed. Actions artifacts expire after 14 days; rebuild this firmware and
pass the new successful run ID to the main repository's menu workflow when needed.

No entry, panic-screen or hardware probe payload is added by this port.

License: BSD-2-Clause-Patent.
