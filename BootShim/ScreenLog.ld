ENTRY(_Head)
SECTIONS {
  . = 0;
  .text : { *(.text) *(.text.*) }
  .rodata : { *(.rodata*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  . = ALIGN(16);
  .stack : { BYTE(0); . += 0x7fff; }
  _ScreenStackTop = .;
  . = ALIGN(16);
  _Payload = .;
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
