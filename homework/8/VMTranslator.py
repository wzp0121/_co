import sys
import os

# ------------------------------------------------------------
# Parser：負責讀取 VM 檔案、逐行解析
# ------------------------------------------------------------
class Parser:
    def __init__(self, file_path):
        self.file = open(file_path, "r")
        self.lines = self.file.readlines()
        self.current_command = None
        self.index = -1

    def hasMoreCommands(self):
        return self.index + 1 < len(self.lines)

    def advance(self):
        while True:
            self.index += 1
            if self.index >= len(self.lines):
                return False
            line = self.lines[self.index]
            line = line.strip()
            line = line.split("//")[0].strip()
            if line != "":
                self.current_command = line
                return True
        return False

    def commandType(self):
        c = self.current_command
        if c.startswith("push"):
            return "C_PUSH"
        elif c.startswith("pop"):
            return "C_POP"
        elif c in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return "C_ARITHMETIC"
        else:
            return "C_UNKNOWN"

    def arg1(self):
        if self.commandType() == "C_ARITHMETIC":
            return self.current_command
        return self.current_command.split()[1]

    def arg2(self):
        return int(self.current_command.split()[2])


# ------------------------------------------------------------
# CodeWriter：負責把 VM 指令寫成 Hack 組合語言
# ------------------------------------------------------------
class CodeWriter:
    def __init__(self, output_path):
        self.file = open(output_path, "w")
        self.filename = None
        self.label_counter = 0

    def setFileName(self, filename):
        self.filename = filename

    # --------------------------------------------------------
    # 處理算術邏輯指令
    # --------------------------------------------------------
    def writeArithmetic(self, command):
        asm = []

        # 基本二元運算（add, sub, and, or）
        if command in ["add", "sub", "and", "or"]:
            asm += [
                "@SP", "AM=M-1", "D=M",  # y = pop
                "A=A-1"                  # x = top
            ]
            if command == "add":
                asm.append("M=M+D")
            elif command == "sub":
                asm.append("M=M-D")
            elif command == "and":
                asm.append("M=M&D")
            elif command == "or":
                asm.append("M=M|D")

        # 單元運算 neg, not
        elif command == "neg":
            asm += ["@SP", "A=M-1", "M=-M"]
        elif command == "not":
            asm += ["@SP", "A=M-1", "M=!M"]

        # 比較運算 eq, gt, lt
        elif command in ["eq", "gt", "lt"]:
            label_true = f"TRUE_{self.label_counter}"
            label_end = f"END_{self.label_counter}"
            self.label_counter += 1

            asm += [
                "@SP", "AM=M-1", "D=M",  # y
                "A=A-1", "D=M-D",        # x-y
                f"@{label_true}"
            ]

            if command == "eq":
                asm.append("D;JEQ")
            elif command == "gt":
                asm.append("D;JGT")
            elif command == "lt":
                asm.append("D;JLT")

            asm += [
                "@SP", "A=M-1", "M=0",   # false
                f"@{label_end}", "0;JMP",
                f"({label_true})",
                "@SP", "A=M-1", "M=-1",  # true
                f"({label_end})"
            ]

        self._write(asm)

    # --------------------------------------------------------
    # 處理 push/pop
    # --------------------------------------------------------
    def writePushPop(self, command, segment, index):
        asm = []
        if command == "C_PUSH":
            if segment == "constant":
                asm += [
                    f"@{index}", "D=A",
                    "@SP", "A=M", "M=D",
                    "@SP", "M=M+1"
                ]
            # 其他 segment（local, argument, this, that, temp, pointer, static）
            # 你可以在這裡依照需求持續補完
            # --------------------------------------------------
            else:
                pass

        elif command == "C_POP":
            # 你在此填寫 pop 對應 segment 的處理
            pass

        self._write(asm)

    # --------------------------------------------------------
    # 寫入指令
    # --------------------------------------------------------
    def _write(self, lines):
        for line in lines:
            self.file.write(line + "\n")

    def close(self):
        self.file.close()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py input.vm")
        return

    input_path = sys.argv[1]

    if input_path.endswith(".vm"):
        files = [input_path]
        out_path = input_path.replace(".vm", ".asm")
    else:
        # 輸入一個資料夾
        files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".vm")]
        out_path = os.path.join(input_path, input_path.split("/")[-1] + ".asm")

    code_writer = CodeWriter(out_path)

    for file in files:
        parser = Parser(file)
        code_writer.setFileName(os.path.basename(file).replace(".vm", ""))

        while parser.hasMoreCommands():
            if not parser.advance():
                continue

            ctype = parser.commandType()

            if ctype == "C_ARITHMETIC":
                code_writer.writeArithmetic(parser.arg1())

            elif ctype in ["C_PUSH", "C_POP"]:
                code_writer.writePushPop(
                    ctype,
                    parser.arg1(),
                    parser.arg2()
                )

    code_writer.close()


if __name__ == "__main__":
    main()