import ast


def detect_long_parameters(code: str, threshold: int = 3) -> dict:
    codeTree = ast.parse(code)
    longParams = {}
    
    for node in ast.walk(codeTree):
        if isinstance(node, ast.FunctionDef):
            funcName = node.name
            paramCount = len(node.args.args)
            if paramCount > threshold:
                longParams[funcName] = paramCount
                
    return longParams
