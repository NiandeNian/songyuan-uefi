/* Based on Mu-Silicium BootShim. SPDX-License-Identifier: BSD-2-Clause-Patent */
_Head:
#if SONGYUAN_SCREEN_LOG
  b     _Start
  .long 0
#else
  adr   x1, _Payload
  b     _Start
#endif

#if REQUIRES_KERNEL_HEADER == 1
  .quad FD_BASE
#if SONGYUAN_SCREEN_LOG
  .quad 0 /* Patched after the diagnostic shim is linked. */
#else
  .quad FD_SIZE + _Payload - _Head
#endif
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
#if SONGYUAN_SCREEN_LOG
  mov   x19, x0
  adr   x1, _ScreenStackTop
  mov   sp, x1
  adr   x1, _ScreenVectors
  mrs   x20, CurrentEL
  cmp   x20, #8
  b.eq  1f
  msr   vbar_el1, x1
  mrs   x1, sctlr_el1
  b     2f
1:
  msr   vbar_el2, x1
  mrs   x1, sctlr_el2
2:
  isb
  mov   x0, x20
  mov   x2, x19
  adr   x3, _Head
  bl    songyuan_screen_start
  adr   x0, .Lcopy_message
  mov   x1, #4
  bl    songyuan_screen_line
  adr   x1, _Payload
#endif
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
#if SONGYUAN_SCREEN_LOG
  adr   x0, .Lentry_message
  mov   x1, #5
  bl    songyuan_screen_line
  mov   x0, x19
  ldr   x5, =FD_BASE
#endif
  br    x5

_Dead:
  b     _Dead

.text
.align 4
#if SONGYUAN_SCREEN_LOG
  .global _Head
  .extern _Payload
  .extern _ScreenStackTop

  /* Retain the error on screen rather than resetting before it can be read. */
  .balign 0x800
_ScreenVectors:
  .rept 16
    b _ScreenFault
    .balign 0x80
  .endr
_ScreenFault:
  msr daifset, #0xf
  msr spsel, #1
  adr x4, _ScreenStackTop
  mov sp, x4
  mrs x4, CurrentEL
  cmp x4, #8
  b.eq 3f
  mrs x0, esr_el1
  mrs x1, elr_el1
  mrs x2, far_el1
  b 4f
3:
  mrs x0, esr_el2
  mrs x1, elr_el2
  mrs x2, far_el2
4:
  bl songyuan_screen_fault
5:
  wfe
  b 5b
.section .rodata
.Lcopy_message:
  .asciz "[4] Copying firmware to 0xA7100000"
.Lentry_message:
  .asciz "[5] FD copied; cache synchronized; entering SEC"
#else
_Payload:
#endif
