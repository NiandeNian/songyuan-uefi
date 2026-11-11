"""Add explicit SEC stage messages to the pinned Mu source for DEBUG builds."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mu-root', type=Path, required=True)
args = parser.parse_args()
path = args.mu_root / 'Silicon/Silicium/SiliciumPkg/Sec/Sec.c'
source = path.read_text()
edits = [
    ('#include "Sec.h"', '#include "Sec.h"\nextern void songyuan_screen_line(const char *, unsigned);\nextern void songyuan_screen_thread(unsigned);'),
    ('  ArmDisableDataCache ();', '  songyuan_screen_line("[7] SecEntry: disable D-cache", 7);\n  ArmDisableDataCache ();'),
    ('  ArmInvalidateInstructionCache ();', '  songyuan_screen_line("[8] D-cache off; invalidate I-cache", 8);\n  ArmInvalidateInstructionCache ();'),
    ('  ArmEnableInstructionCache ();', '  ArmEnableInstructionCache ();\n  songyuan_screen_line("[9] I-cache ready; invalidate stack/FD", 9);'),
    ('  ArmWriteVBar ((UINTN)SecVectorTable);', '  ArmWriteVBar ((UINTN)SecVectorTable);\n  songyuan_screen_line("[10] SEC exception vectors installed", 10);'),
    ('  PlatformInitialize ();', '  songyuan_screen_line("[11] SecMain: platform handoff", 11);\n  PlatformInitialize ();'),
    ('  Status = InitializeMemory ();', '  songyuan_screen_line("[12] InitializeMemory: HOB and MMU", 12);\n  songyuan_screen_line("Thread before MMU:", 29);\n  songyuan_screen_thread(30);\n  Status = InitializeMemory ();'),
    ('  // Build CPU HOB', '  songyuan_screen_line("[13] Memory/MMU initialized", 13);\n  songyuan_screen_line("Thread after MMU:", 31);\n  songyuan_screen_thread(32);\n\n  // Build CPU HOB'),
    ('  Status = PlatformPeim ();', '  songyuan_screen_line("[14] PlatformPeim: stock XBL HOBs", 14);\n  Status = PlatformPeim ();'),
    ('  ProcessLibraryConstructorList ();', '  songyuan_screen_line("[15] XBL HOBs ready; constructors", 15);\n  ProcessLibraryConstructorList ();'),
    ('  Status = DecompressFirstFv ();', '  songyuan_screen_line("[16] Decompress firmware volume", 16);\n  Status = DecompressFirstFv ();'),
    ('  Status = LoadDxeCoreFromFv (NULL, 0);', '  songyuan_screen_line("[17] Firmware ready; load DXE core", 17);\n  Status = LoadDxeCoreFromFv (NULL, 0);'),
]
for before, after in edits:
    if source.count(before) != 1:
        raise SystemExit('Pinned SEC source differs or was already instrumented: ' + before)
    source = source.replace(before, after, 1)
path.write_text(source)
print('Applied 11 explicit SEC screen stages to the pinned source')

# The SEC exception routine otherwise prints only PC. Preserve ESR/FAR and the
# live thread register without dereferencing the potentially unmapped thread.
path = args.mu_root / 'Silicon/Silicium/SiliciumPkg/Sec/AArch64/ArchSec.c'
source = path.read_text()
before = '  // CPU Dead Loop'
if source.count(before) != 1:
    raise SystemExit('Pinned SEC exception source differs')
source = source.replace('#include "Sec.h"', '#include "Sec.h"\nextern void songyuan_screen_sec_fault(UINT64, UINT64);', 1)
source = source.replace(before, '  songyuan_screen_sec_fault(Type, LR);\n\n' + before, 1)
path.write_text(source)

# Separate static GUID discovery from the first call into the stock scheduler.
path = args.mu_root / 'Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/PlatformPei.c'
source = path.read_text()
source = source.replace('#include "PlatformPei.h"', '#include "PlatformPei.h"\nextern void songyuan_screen_line(const char *, unsigned);\nextern void songyuan_screen_hex(const char *, UINT64, unsigned);', 1)
edits = [
    ('  // Build XBL HOBs', '  songyuan_screen_hex("XBL scheduler", SchedulerInterfaceAddr, 33);\n  songyuan_screen_hex("XBL DTB extension", DtbExtensionAddr, 34);\n\n  // Build XBL HOBs'),
    ('    // Create FV List', '    songyuan_screen_hex("Scheduler Lock table", (UINTN)SchedulerProtocol->Lock, 35);\n    songyuan_screen_hex("Scheduler InitLock", (UINTN)SchedulerProtocol->Lock->InitLock, 36);\n\n    // Create FV List'),
    ('    Status = SchedulerProtocol->Lock->InitLock (FvEntryName, &FvEntryHandle);', '    songyuan_screen_hex("FV InitLock entry", i, 37);\n    Status = SchedulerProtocol->Lock->InitLock (FvEntryName, &FvEntryHandle);'),
    ('    // Add FV Entry Lock Handle', '    songyuan_screen_line("FV InitLock returned", 38);\n\n    // Add FV Entry Lock Handle'),
]
for before, after in edits:
    if source.count(before) != 1:
        raise SystemExit('Pinned PlatformPei source differs: ' + before)
    source = source.replace(before, after, 1)
path.write_text(source)
print('Added XBL call stages and SEC ESR/FAR/TPIDR diagnostics')
