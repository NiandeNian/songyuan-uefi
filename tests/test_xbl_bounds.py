"""Exercise the actual C scanner against an inaccessible page after the FD.

Run on Linux/WSL with a host C compiler. --original accepts the pinned upstream
file for a negative control: its empty-region scan must fault at the guard page.
"""
from pathlib import Path
import argparse, os, subprocess, tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--original', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
header = r'''
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
#include <unistd.h>
#define IN
#define OUT
#define STATIC static
#define VOID void
#define TRUE 1
#define FALSE 0
#define MAX_UINT64 UINT64_MAX
#define EFI_ERROR(x) ((x) != 0)
typedef uint32_t UINT32;
typedef uint64_t UINT64;
typedef int32_t INT32;
typedef int64_t INT64;
typedef int BOOLEAN;
typedef int EFI_STATUS;
typedef uint64_t EFI_PHYSICAL_ADDRESS;
typedef struct { uint8_t bytes[16]; } EFI_GUID;
typedef struct { uint64_t Address, Length; } EFI_MEMORY_REGION_DESCRIPTOR;
static EFI_MEMORY_REGION_DESCRIPTOR region;
static EFI_GUID gEfiSchedulerInterfaceHobGuid = {{1,2,3,4}};
static EFI_GUID gEfiDtbExtensionHobGuid = {{9,8,7,6}};
static int LocateMemoryRegionByName(const char *name, EFI_MEMORY_REGION_DESCRIPTOR *r) {
  if (strcmp(name, "FD_Reserved") != 0) return 1;
  *r = region; return 0;
}
static int CompareGuid(const EFI_GUID *a, const EFI_GUID *b) {
  return memcmp(a, b, sizeof(*a)) == 0;
}
#define ARM64_INSTRUCTION_LENGTH 4
#define ARM64_TOTAL_INSTRUCTION_LENGTH(n) ((n) * 4)
#define ARM64_INSTRUCTION(a) (*(uint32_t *)(uintptr_t)(a))
'''
common = r'''
static unsigned char *guarded(size_t *page) {
  *page = (size_t)sysconf(_SC_PAGESIZE);
  unsigned char *p = mmap(NULL, *page * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  assert(p != MAP_FAILED);
  assert(mprotect(p + *page, *page, PROT_NONE) == 0);
  region.Address = (uintptr_t)p; region.Length = *page;
  return p;
}
static void scan_empty(void) {
  uint64_t scheduler = 0, dtb = 0;
  GetXblHobAddresses(&scheduler, &dtb);
  assert(scheduler == 0 && dtb == 0);
}
'''
cases = r'''
static uint32_t adrp(unsigned rd, int pages) {
  uint32_t imm = (uint32_t)pages & 0x1fffff;
  return 0x90000000 | (imm & 3) << 29 | (imm >> 2) << 5 | rd;
}
static uint32_t add(unsigned rd, unsigned rn, unsigned offset) {
  return 0x91000000 | offset << 10 | rn << 5 | rd;
}
static void signature(unsigned char *p) {
  *(uint32_t *)(p+0) = 0xd10083ff;
  *(uint32_t *)(p+4) = 0xa9017bfd;
  *(uint32_t *)(p+32) = 0x52800100;
}
int main(void) {
  size_t page;
  unsigned char *p = guarded(&page);
  scan_empty();                         // Original scanner reads page+0 here.
  *(uint32_t *)(p+page-8) = 0xd10083ff; // Partial prologue; no ninth instruction.
  *(uint32_t *)(p+page-4) = 0xa9017bfd;
  scan_empty();
  memset(p, 0, page);
  signature(p + page - 36);              // Complete prologue, but no RET.
  scan_empty();
  memset(p, 0, page);
  signature(p + 4);                     // Four-byte alignment is enough.
  *(uint32_t *)(p+44) = adrp(0, 0);
  *(uint32_t *)(p+48) = add(1, 0, 128);  // Rd != Rn: GUID via a different register.
  *(uint32_t *)(p+52) = adrp(2, 0);
  *(uint32_t *)(p+56) = add(2, 2, 256);
  *(uint32_t *)(p+60) = 0xd65f03c0;
  memcpy(p+128, &gEfiSchedulerInterfaceHobGuid, 16);
  uint64_t scheduler = 0, dtb = 0;
  GetXblHobAddresses(&scheduler, &dtb);
  assert(scheduler == (uintptr_t)(p+256) && dtb == 0);
  *(uint32_t *)(p+44) = adrp(0, 1);      // GUID address points into guard page.
  scan_empty();
  *(uint32_t *)(p+44) = adrp(0, 0);
  *(uint32_t *)(p+48) = add(1, 0, page-8); // Only half a GUID is readable.
  scan_empty();
  EFI_PHYSICAL_ADDRESS base;
  uint32_t reg;
  ParseAdrpInstruction(adrp(3, -1), (uintptr_t)p, &base, &reg);
  assert(base == (uintptr_t)p - page && reg == 3);
  region.Length = 8; scan_empty();
  region.Address = UINT64_MAX - 15; region.Length = 64; scan_empty();
  region.Address = (uintptr_t)p + 1; region.Length = page - 1; scan_empty();
  puts("PASS: tail, lookahead, missing RET, guarded GUID, ADD Rn, negative ADRP, invalid ranges");
  return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='songyuan-xbl-') as name:
    work = Path(name)
    (work/'Library').mkdir()
    for lib in ('MemoryMapHelperLib', 'AssemblyUtilsLib', 'BaseMemoryLib'):
        (work/'Library'/(lib+'.h')).write_text('/* host shim */\n')
    def compile_run(source, main, label, sanitize=True):
        path = work/(label+'.c')
        path.write_text(header + '\n' + source + '\n' + common + '\n' + main)
        binary = work/label
        command = [os.environ.get('CC', 'cc'), '-std=c11', '-D_GNU_SOURCE', '-Wall', '-Wextra', '-Werror', '-I'+str(work), str(path), '-o', str(binary)]
        if sanitize:
            command += ['-fsanitize=undefined', '-fno-sanitize-recover=all']
        subprocess.run(command, check=True)
        return subprocess.run([str(binary)], capture_output=True, text=True)
    fixed = compile_run((root/'Patches/XblProtocols.c').read_text(), cases, 'fixed')
    print(fixed.stdout, end='')
    if fixed.returncode:
        raise SystemExit(fixed.stderr or 'Fixed scanner failed: '+str(fixed.returncode))
    if args.original:
        original_main = 'int main(void) { size_t page; guarded(&page); scan_empty(); return 0; }'
        original = compile_run(args.original.read_text(), original_main, 'original', sanitize=False)
        assert original.returncode == -11, (original.returncode, original.stderr)
        print('PASS: pinned original faults at the guard page (SIGSEGV negative control)')
