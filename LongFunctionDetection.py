import ast

def detect_long_functions(code, threshold = 15):
    codeTree = ast.parse(code)
    longFuncs = {}
    all_lines = code.splitlines()
    
    for node in ast.walk(codeTree):
        if isinstance(node, ast.FunctionDef):
            funcName = node.name
            startLine = node.lineno
            endLine = node.end_lineno
            
            functionLines = all_lines[startLine - 1 : endLine]
            totalFuncLines = sum(1 for line in functionLines if line.strip() != "")
            
            if totalFuncLines > threshold:
                longFuncs[funcName] = totalFuncLines
                
    return longFuncs