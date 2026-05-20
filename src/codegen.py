
from src.intermediate import TACInstruction


class TargetCodeGenerator:
   

    def __init__(self):
        self.assembly = []
        self.data_section = []
        self.string_literals = {}
        self.string_count = 0

    def generate(self, instructions):
        self.assembly.append("; ==============================")
        self.assembly.append("; Arabic Compiler - Target Code")
        self.assembly.append("; ==============================")
        self.assembly.append("")
        self.assembly.append("section .data")

        for instr in instructions:
            if instr.arg1 and isinstance(instr.arg1, str) and instr.arg1.startswith('"'):
                self._register_string(instr.arg1)
            if instr.arg2 and isinstance(instr.arg2, str) and instr.arg2.startswith('"'):
                self._register_string(instr.arg2)

        for label, value in self.string_literals.items():
            self.assembly.append(f"  {label}: db {value}, 0")

        self.assembly.append("")
        self.assembly.append("section .text")
        self.assembly.append("  global _start")
        self.assembly.append("")
        self.assembly.append("_start:")

        for instr in instructions:
            self._translate(instr)

        self.assembly.append("")
        self.assembly.append("  ; Exit program")
        self.assembly.append("  MOV EAX, 1        ; sys_exit")
        self.assembly.append("  XOR EBX, EBX      ; exit code 0")
        self.assembly.append("  INT 0x80")

        return self.assembly

    def _register_string(self, s):
        """Register a string literal and return its label"""
        if s not in self.string_literals:
            label = f"str_{self.string_count}"
            self.string_literals[s] = label
            self.string_count += 1
        return self.string_literals[s]

    def _translate(self, instr):
        """Translate a single TAC instruction to assembly"""

        if instr.op == 'LABEL':
            self.assembly.append(f"\n{instr.result}:")

        elif instr.op == 'ASSIGN':
            if instr.arg1 and instr.arg1.startswith('"'):
                label = self._register_string(instr.arg1)
                self.assembly.append(f"  LEA EAX, [{label}]  ; {instr.result} = {instr.arg1}")
                self.assembly.append(f"  MOV [{instr.result}], EAX")
            else:
                self.assembly.append(f"  MOV EAX, {instr.arg1}       ; load {instr.arg1}")
                self.assembly.append(f"  MOV [{instr.result}], EAX   ; {instr.result} = {instr.arg1}")

        elif instr.op == '+':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load {instr.arg1}")
            self.assembly.append(f"  ADD EAX, [{instr.arg2}]     ; + {instr.arg2}")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store in {instr.result}")

        elif instr.op == '-':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load {instr.arg1}")
            self.assembly.append(f"  SUB EAX, [{instr.arg2}]     ; - {instr.arg2}")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store in {instr.result}")

        elif instr.op == '*':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load {instr.arg1}")
            self.assembly.append(f"  IMUL EAX, [{instr.arg2}]    ; * {instr.arg2}")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store in {instr.result}")

        elif instr.op == '/':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load dividend")
            self.assembly.append(f"  CDQ                          ; sign extend")
            self.assembly.append(f"  IDIV DWORD [{instr.arg2}]   ; / {instr.arg2}")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store quotient")

        elif instr.op == '%':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load dividend")
            self.assembly.append(f"  CDQ                          ; sign extend")
            self.assembly.append(f"  IDIV DWORD [{instr.arg2}]   ; % {instr.arg2}")
            self.assembly.append(f"  MOV [{instr.result}], EDX   ; store remainder")

        elif instr.op in ('==', '!=', '<', '>', '<=', '>='):
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load left")
            self.assembly.append(f"  CMP EAX, [{instr.arg2}]     ; compare with right")
            jmp_map = {'==': 'SETE', '!=': 'SETNE', '<': 'SETL',
                       '>': 'SETG', '<=': 'SETLE', '>=': 'SETGE'}
            self.assembly.append(f"  {jmp_map[instr.op]} AL              ; set flag")
            self.assembly.append(f"  MOVZX EAX, AL")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store boolean result")

        elif instr.op == 'UMINUS':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load operand")
            self.assembly.append(f"  NEG EAX                      ; negate")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store result")

        elif instr.op == 'NOT':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load operand")
            self.assembly.append(f"  XOR EAX, 1                   ; logical NOT")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store result")

        elif instr.op == 'wa':  # AND
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load left")
            self.assembly.append(f"  AND EAX, [{instr.arg2}]     ; logical AND")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store result")

        elif instr.op == 'aw':  # OR
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load left")
            self.assembly.append(f"  OR EAX, [{instr.arg2}]      ; logical OR")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store result")

        elif instr.op == 'GOTO':
            self.assembly.append(f"  JMP {instr.result}           ; jump to {instr.result}")

        elif instr.op == 'IF_TRUE':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load condition")
            self.assembly.append(f"  CMP EAX, 1")
            self.assembly.append(f"  JE {instr.result}            ; jump if true")

        elif instr.op == 'IF_FALSE':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load condition")
            self.assembly.append(f"  CMP EAX, 0")
            self.assembly.append(f"  JE {instr.result}            ; jump if false")

        elif instr.op == 'PRINT':
            if instr.arg1 and instr.arg1.startswith('"'):
                label = self._register_string(instr.arg1)
                self.assembly.append(f"  ; --- PRINT string ---")
                self.assembly.append(f"  MOV EAX, 4        ; sys_write")
                self.assembly.append(f"  MOV EBX, 1        ; stdout")
                self.assembly.append(f"  LEA ECX, [{label}] ; string address")
                self.assembly.append(f"  MOV EDX, {len(instr.arg1)-2}  ; string length")
                self.assembly.append(f"  INT 0x80")
            else:
                self.assembly.append(f"  ; --- PRINT {instr.arg1} ---")
                self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; load value")
                self.assembly.append(f"  CALL __print_int             ; print integer")

        elif instr.op == 'FUNC_BEGIN':
            self.assembly.append(f"\n{instr.arg1}:")
            self.assembly.append(f"  PUSH EBP                     ; save base pointer")
            self.assembly.append(f"  MOV EBP, ESP                 ; set new base")

        elif instr.op == 'FUNC_END':
            self.assembly.append(f"  MOV ESP, EBP                 ; restore stack")
            self.assembly.append(f"  POP EBP                      ; restore base pointer")
            self.assembly.append(f"  RET                           ; return")

        elif instr.op == 'PARAM':
            self.assembly.append(f"  PUSH [{instr.arg1}]          ; push param {instr.arg1}")

        elif instr.op == 'CALL':
            self.assembly.append(f"  CALL {instr.arg1}            ; call function {instr.arg1}")
            self.assembly.append(f"  ADD ESP, {int(instr.arg2) * 4}  ; cleanup {instr.arg2} params")
            self.assembly.append(f"  MOV [{instr.result}], EAX   ; store return value")

        elif instr.op == 'RETURN':
            self.assembly.append(f"  MOV EAX, [{instr.arg1}]     ; return value")
            self.assembly.append(f"  MOV ESP, EBP")
            self.assembly.append(f"  POP EBP")
            self.assembly.append(f"  RET")
