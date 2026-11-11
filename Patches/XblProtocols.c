// SPDX-License-Identifier: BSD-2-Clause-Patent
// Bounded variant of the pinned Mu-Silicium XBL protocol scanner.
#include <Library/MemoryMapHelperLib.h>
#include <Library/AssemblyUtilsLib.h>
#include <Library/BaseMemoryLib.h>

STATIC BOOLEAN
FdContains (
  IN EFI_PHYSICAL_ADDRESS Base,
  IN EFI_PHYSICAL_ADDRESS End,
  IN EFI_PHYSICAL_ADDRESS Address,
  IN UINT64               Length)
{
  return Address >= Base && Address <= End && Length <= End - Address;
}

VOID
ParseAdrpInstruction (
  IN  UINT32                Instruction,
  IN  UINT64                InstructionLocation,
  OUT EFI_PHYSICAL_ADDRESS *BaseAddress,
  OUT UINT32               *Register)
{
  UINT32 ImmHi = (Instruction >> 5) & 0x7FFFF;
  UINT32 ImmLo = (Instruction >> 29) & 0x3;
  INT32  Imm21 = (ImmHi << 2) | ImmLo;

  if (Imm21 & 0x100000) {
    Imm21 |= 0xFFE00000;
  }
  // Multiplication also handles a negative ADRP offset without signed-shift UB.
  *BaseAddress = (InstructionLocation & ~0xFFFULL) + (INT64)Imm21 * 4096;
  *Register = Instruction & 0x1F;
}

VOID
ParseAddInstruction (
  IN  UINT32  Instruction,
  OUT UINT32 *AddressOffset,
  OUT UINT32 *SourceRegister,
  OUT UINT32 *TargetRegister)
{
  *AddressOffset  = (Instruction >> 10) & 0xFFF;
  *SourceRegister = (Instruction >> 5) & 0x1F;
  *TargetRegister = Instruction & 0x1F;
}

STATIC EFI_PHYSICAL_ADDRESS
ParseHobFunction (
  IN EFI_PHYSICAL_ADDRESS  FunctionStart,
  IN EFI_PHYSICAL_ADDRESS  FdBase,
  IN EFI_PHYSICAL_ADDRESS  FdEnd,
  IN EFI_GUID             *ProtocolGuid)
{
  EFI_PHYSICAL_ADDRESS ProtocolAddress = 0;
  UINT64               AdrpRegValue[32] = {0};
  BOOLEAN              GuidMatched = FALSE;

  // A missing RET must never walk into the next unmapped page.
  for (EFI_PHYSICAL_ADDRESS Current = FunctionStart;
       FdContains (FdBase, FdEnd, Current, ARM64_INSTRUCTION_LENGTH);
       Current += ARM64_INSTRUCTION_LENGTH) {
    UINT32 Instruction = ARM64_INSTRUCTION (Current);

    if (Instruction == 0xD65F03C0) {
      return GuidMatched ? ProtocolAddress : 0;
    }
    if ((Instruction & 0x9F000000) == 0x90000000) {
      EFI_PHYSICAL_ADDRESS BaseAddress;
      UINT32 Register;
      ParseAdrpInstruction (Instruction, Current, &BaseAddress, &Register);
      AdrpRegValue[Register] = BaseAddress;
    }
    if ((Instruction & 0xFFC00000) == 0x91000000) {
      UINT32 AddressOffset;
      UINT32 SourceRegister;
      UINT32 TargetRegister;
      ParseAddInstruction (Instruction, &AddressOffset, &SourceRegister, &TargetRegister);

      // ADD reads Rn, including when Rd differs from Rn.
      if (AdrpRegValue[SourceRegister] == 0) {
        AdrpRegValue[TargetRegister] = 0;
        continue;
      }
      AdrpRegValue[TargetRegister] = AdrpRegValue[SourceRegister] + AddressOffset;

      // ADRP/ADD can describe MMIO or an address outside the retained image.
      // Do not dereference those addresses while looking for a GUID.
      if (!FdContains (FdBase, FdEnd, AdrpRegValue[TargetRegister], sizeof (EFI_GUID))) {
        continue;
      }
      if (CompareGuid ((EFI_GUID *)AdrpRegValue[TargetRegister], ProtocolGuid)) {
        GuidMatched = TRUE;
        continue;
      }
      ProtocolAddress = AdrpRegValue[TargetRegister];
    }
  }
  return 0;
}

VOID
GetXblHobAddresses (
  OUT EFI_PHYSICAL_ADDRESS *SchedulerInterfaceAddr,
  OUT EFI_PHYSICAL_ADDRESS *DtbExtensionAddr)
{
  EFI_MEMORY_REGION_DESCRIPTOR ReservedFd = {0};
  EFI_PHYSICAL_ADDRESS         End;
  EFI_STATUS                   Status;
  UINT64                       SignatureLength = ARM64_TOTAL_INSTRUCTION_LENGTH (8) + ARM64_INSTRUCTION_LENGTH;

  Status = LocateMemoryRegionByName ("FD Reserved", &ReservedFd);
  if (EFI_ERROR (Status)) {
    Status = LocateMemoryRegionByName ("FD_Reserved", &ReservedFd);
  }
  if (EFI_ERROR (Status) || ReservedFd.Address == 0 ||
      ReservedFd.Length < SignatureLength ||
      ReservedFd.Length > MAX_UINT64 - ReservedFd.Address ||
      (ReservedFd.Address & (ARM64_INSTRUCTION_LENGTH - 1)) != 0) {
    return;
  }
  End = ReservedFd.Address + ReservedFd.Length;

  for (EFI_PHYSICAL_ADDRESS Current = ReservedFd.Address;
       FdContains (ReservedFd.Address, End, Current, SignatureLength);
       Current += ARM64_INSTRUCTION_LENGTH) {
    // Two instruction reads avoid an unaligned UINT64 load at Current % 8 == 4.
    if (ARM64_INSTRUCTION (Current) != 0xD10083FF ||
        ARM64_INSTRUCTION (Current + ARM64_INSTRUCTION_LENGTH) != 0xA9017BFD) {
      continue;
    }
    if ((ARM64_INSTRUCTION (Current + ARM64_TOTAL_INSTRUCTION_LENGTH (8)) & 0xFFFFFFE0) != 0x52800100) {
      continue;
    }
    if (*SchedulerInterfaceAddr == 0) {
      *SchedulerInterfaceAddr = ParseHobFunction (Current, ReservedFd.Address, End, &gEfiSchedulerInterfaceHobGuid);
    }
    if (*DtbExtensionAddr == 0) {
      *DtbExtensionAddr = ParseHobFunction (Current, ReservedFd.Address, End, &gEfiDtbExtensionHobGuid);
    }
    if (*SchedulerInterfaceAddr != 0 && *DtbExtensionAddr != 0) {
      break;
    }
  }
}
