/** SM8850 firmware handoff. SPDX-License-Identifier: BSD-2-Clause-Patent */
#include <Library/PlatformSecLib.h>

VOID
PlatformInitialize (VOID)
{
  // ABL leaves the display and Qualcomm firmware clients running. The menu
  // uses the inherited framebuffer and does not own their DMA contexts.
  // ArmSmmuDetach walks every context bank, including banks without an SMR
  // owned by UEFI, and clears their TTBR/TCR before the MMU and DXE are ready.
  // Keep the stock QSMMUv500 state intact here. A peripheral driver must
  // quiesce its client and take over only its own stream/context bank.
}
