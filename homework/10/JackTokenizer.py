import re
import sys
import os

class JackTokenizer:
    def __init__(self, input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        # 1. 移除註解 (包含 //, /* */, /** */)
        self.content = re.sub(r'//.*?\n|/\*.*?\*/', ' ', self.content, flags=re.DOTALL)
        
        # 2. 定義 Jack 語法標籤
        self.keywords = {'class', 'constructor', 'function', 'method', 'field', 'static', 
                         'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 
                         'this', 'let', 'do', 'if', 'else', 'while', 'return'}
        self.symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
        
        # 3. 使用正規表示式切分 Token
        # 順序：字串常數 | 標識符 | 數字 | 符號
        token_pattern = r'"[^"\n]*"|[a-zA-Z_]\w*|\d+|' + '|'.join(map(re.escape, self.symbols))
        self.tokens = re.findall(token_pattern, self.content)
        self.cursor = 0
        self.current_token = None

    def hasMoreTokens(self):
        return self.cursor < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            self.current_token = self.tokens[self.cursor]
            self.cursor += 1

    def tokenType(self):
        t = self.current_token
        if t in self.keywords: return "keyword"
        if t in self.symbols: return "symbol"
        if t.startswith('"'): return "stringConstant"
        if t.isdigit(): return "integerConstant"
        return "identifier"

def run_analyzer(input_path):
    # 支援傳入單一檔案或整個資料夾
    files_to_process = []
    if os.path.isdir(input_path):
        for f in os.listdir(input_path):
            if f.endswith(".jack"):
                files_to_process.append(os.path.join(input_path, f))
    elif input_path.endswith(".jack"):
        files_to_process.append(input_path)

    specials = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}

    for jack_file in files_to_process:
        # 輸出檔案名稱格式：FileNameT_test.xml
        output_file = jack_file.replace(".jack", "T_test.xml")
        tokenizer = JackTokenizer(jack_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("<tokens>\n")
            while tokenizer.hasMoreTokens():
                tokenizer.advance()
                t_type = tokenizer.tokenType()
                val = tokenizer.current_token
                
                if t_type == "stringConstant":
                    val = val[1:-1] # 移除引號
                elif val in specials:
                    val = specials[val] # 轉換 XML 特殊字元
                
                f.write(f"<{t_type}> {val} </{t_type}>\n")
            f.write("</tokens>\n")
        print(f"已完成編譯：{os.path.basename(jack_file)} -> {os.path.basename(output_file)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python JackTokenizer.py <檔案或資料夾路徑>")
    else:
        run_analyzer(sys.argv[1])