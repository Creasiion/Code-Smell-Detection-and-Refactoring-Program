import ast
import builtins
                
class VariableNormalizer(ast.NodeTransformer):
    def __init__(self):
        self.varMapping = {}
        self.varCounter = 1
        
    def visit_FunctionDef(self, node):
        outerMapping = self.varMapping
        outerCounter = self.varCounter

        self.varMapping = {}
        self.varCounter = 1

        for arg in node.args.args:
            self.visit_arg(arg)

        node.body = [self.visit(stmt) for stmt in node.body]

        self.varMapping = outerMapping
        self.varCounter = outerCounter

        return node

        
    def visit_Name(self, node):
        if node.id in dir(builtins):
            return node
        
        if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
            original = node.id
            if original not in self.varMapping:
                self.varMapping[original] = f"VAR{self.varCounter}"
                self.varCounter += 1
            newName = self.varMapping[original]
            return ast.copy_location(ast.Name(id=newName, ctx=node.ctx), node)
        return node

    def visit_arg(self, node):
        original = node.arg
        
        if original in dir(builtins):
            return node
        
        if original not in self.varMapping:
            self.varMapping[original] = f"VAR{self.varCounter}"
            self.varCounter += 1
        node.arg = self.varMapping[original]
        return node

class RefactoringDuplicates(ast.NodeTransformer):
    def __init__(self, keepName, removeName):
        self.keepName = keepName
        self.removeName = removeName

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.removeName:
            node.func.id = self.keepName
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name == self.removeName:
            return None
        return self.generic_visit(node)

def calc_jaccard(codeA, codeB):
    setA = set(codeA.split())
    setB = set(codeB.split())
    intersection = len(setA.intersection(setB))
    union = len(setA.union(setB))
    return intersection / union if union > 0 else 0.0

def normalize_ast_code(source):
    tree = ast.parse(source)
    normalizer = VariableNormalizer()
    normalizedTree = normalizer.visit(tree)
    ast.fix_missing_locations(normalizedTree)
    return ast.unparse(normalizedTree)

def normalize_funcs(code):
    codeTree = ast.parse(code)
    normFuncs = {}

    for node in ast.walk(codeTree):
        if isinstance(node, ast.FunctionDef):
            funcName = node.name
            funcSrc = ast.get_source_segment(code, node)
            if funcSrc:
                normaFuncCode = normalize_ast_code(funcSrc)
                normFuncs[funcName] = normaFuncCode
    return normFuncs

def detect_duplicate_functions(code, similarity = 0.75):
    normFuncs = normalize_funcs(code)
    duplicates = {}
    funcNames = list(normFuncs.keys())
    for i in range(len(funcNames)):
        for j in range(i + 1, len(funcNames)):
            n1, n2 = funcNames[i], funcNames[j]
            body1 = normFuncs[n1]
            body2 = normFuncs[n2]
            jaccard = calc_jaccard(body1, body2)
            if jaccard >= similarity:
                duplicates[(n1, n2)] = jaccard

    return duplicates

def refactor_duplicate_functions(code, keepFunc, removeFunc):
    oldTree = ast.parse(code)
    fixer = RefactoringDuplicates(keepFunc, removeFunc)
    newTree = fixer.visit(oldTree)
    ast.fix_missing_locations(newTree)
    return ast.unparse(newTree)

