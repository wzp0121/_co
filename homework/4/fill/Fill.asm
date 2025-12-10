// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// Fill.asm -- fill screen while any key is pressed, clear when none

// RAM usage:
// R0 -> current screen address (pointer)
// R1 -> screen end address (SCREEN + 8192) == 24576
// R2 -> value -1 (for filling)

@24576     // initialize SCREEN_END = 24576 (also KBD address)
D=A
@R1
M=D

// store -1 into R2 for fast writes
@1
D=A
D=-D
@R2
M=D

(LOOP)
  // check keyboard: if zero -> CLEAR, else -> FILL
  @24576
  D=M
  @CLEAR
  D;JEQ

  @FILL
  0;JMP

(FILL)
  @16384
  D=A
  @R0
  M=D

(FILL_LOOP)

  @R2
  D=M
  @R0
  A=M
  M=D

  @R0
  M=M+1

  @R1
  D=M
  @R0
  D=D-M
  @FILL_LOOP
  D;JGT

  @LOOP
  0;JMP

(CLEAR)

  @16384
  D=A
  @R0
  M=D

(CLEAR_LOOP)
  @R0
  A=M
  M=0

  @R0
  M=M+1

  @R1
  D=M
  @R0
  D=D-M
  @CLEAR_LOOP
  D;JGT


  @LOOP
  0;JMP
