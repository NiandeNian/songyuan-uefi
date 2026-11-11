/* Based on Mu-Silicium BootShim. SPDX-License-Identifier: BSD-2-Clause-Patent */
_Head:
  adr   x1, _Payload
  b     _Start

#if REQUIRES_KERNEL_HEADER == 1
  .quad FD_BASE
  .quad FD_SIZE + _Payload - _Head
  .quad 0
  .quad 0, 0, 0
  .ascii "ARM\x64"
  .long 0
#endif

_Start:
  /* Match the known working songyuan loader's architectural entry state.
   * Keep interrupts masked until SEC installs vectors and configures the GIC.
   * SEC's stack must use SP_ELx rather than inheriting a bootloader SP_EL0. */
  msr   daifset, #0xf
  msr   spsel, #1
  isb
  mov   x4, x1
  ldr   x5, =FD_BASE
  cmp   x4, x5
  beq   _Entry
  ldr   x6, =FD_SIZE

_CopyLoop:
  ldp   x2, x3, [x4], #16
  stp   x2, x3, [x5], #16
  subs  x6, x6, #16
  b.ne  _CopyLoop
  ldr   x5, =FD_BASE

_Entry:
  /* ABL's Linux Image handoff has the MMU and D-cache off. Complete the
   * physical FD copy and discard stale instruction lines before executing
   * at FD_BASE; SEC's later cache maintenance cannot protect its own entry. */
  dsb   sy
  ic    iallu
  dsb   sy
  isb
  br    x5

_Dead:
  b     _Dead

.text
.align 4
_Payload:
