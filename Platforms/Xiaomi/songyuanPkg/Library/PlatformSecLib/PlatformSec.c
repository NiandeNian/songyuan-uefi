/** SM8850 display handoff. SPDX-License-Identifier: BSD-2-Clause-Patent */
#include <Library/PlatformSecLib.h>
#include <Library/ArmSmmuDetachLib.h>

VOID
PlatformInitialize (VOID)
{
  // Preserve the live songyuan display mappings while detaching other clients.
  // apps-smmu handoff-smrs = <0x800 0x2>; secure display SID = 0x801.
  // ArmSmmuDetach compares masked SIDs, so 0x800 also covers the 0x802 alias.
  CONST UINT16 DisplayStreams[] = { 0x800, 0x801 };
  ArmSmmuDetach (DisplayStreams, ARRAY_SIZE (DisplayStreams));
}
