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

The FD is a firmware volume; the main repository packages it with BootShim and
a UniXNU payload into an Android header-v0 boot image. The intended boot method
is `fastboot boot`, without replacing Android boot partitions.

## Validation status

Offline validation passes: 76 descriptors, 62 AddMem ranges, no overlaps,
48 songyuan live reservations covered. Hardware boot is pending because the
phone is offline. Inherited OnePlus 15 ACPI and Qualcomm firmware drivers have
not been verified on this phone. CI results are recorded separately from hardware results.

No entry, panic-screen or hardware probe payload is added by this port.

License: BSD-2-Clause-Patent.
