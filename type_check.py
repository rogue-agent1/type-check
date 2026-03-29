#!/usr/bin/env python3
"""type_check: Simple type checker for a typed lambda calculus."""
import sys

class Type:
    pass
class TInt(Type):
    def __repr__(self): return "Int"
    def __eq__(self, o): return isinstance(o, TInt)
    def __hash__(self): return hash("Int")
class TBool(Type):
    def __repr__(self): return "Bool"
    def __eq__(self, o): return isinstance(o, TBool)
    def __hash__(self): return hash("Bool")
class TStr(Type):
    def __repr__(self): return "Str"
    def __eq__(self, o): return isinstance(o, TStr)
    def __hash__(self): return hash("Str")
class TFun(Type):
    def __init__(self, arg, ret): self.arg = arg; self.ret = ret
    def __repr__(self): return f"({self.arg} -> {self.ret})"
    def __eq__(self, o): return isinstance(o, TFun) and self.arg == o.arg and self.ret == o.ret
    def __hash__(self): return hash(("Fun", self.arg, self.ret))
class TList(Type):
    def __init__(self, elem): self.elem = elem
    def __repr__(self): return f"[{self.elem}]"
    def __eq__(self, o): return isinstance(o, TList) and self.elem == o.elem

class Expr:
    pass
class EInt(Expr):
    def __init__(self, val): self.val = val
class EBool(Expr):
    def __init__(self, val): self.val = val
class EStr(Expr):
    def __init__(self, val): self.val = val
class EVar(Expr):
    def __init__(self, name): self.name = name
class ELam(Expr):
    def __init__(self, param, param_type, body): self.param = param; self.param_type = param_type; self.body = body
class EApp(Expr):
    def __init__(self, func, arg): self.func = func; self.arg = arg
class EIf(Expr):
    def __init__(self, cond, then, els): self.cond = cond; self.then = then; self.els = els
class EBinOp(Expr):
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class ELet(Expr):
    def __init__(self, name, val, body): self.name = name; self.val = val; self.body = body

def typecheck(expr, env=None):
    if env is None: env = {}
    if isinstance(expr, EInt): return TInt()
    if isinstance(expr, EBool): return TBool()
    if isinstance(expr, EStr): return TStr()
    if isinstance(expr, EVar):
        if expr.name not in env: raise TypeError(f"Unbound variable: {expr.name}")
        return env[expr.name]
    if isinstance(expr, ELam):
        new_env = {**env, expr.param: expr.param_type}
        ret_type = typecheck(expr.body, new_env)
        return TFun(expr.param_type, ret_type)
    if isinstance(expr, EApp):
        fn_type = typecheck(expr.func, env)
        arg_type = typecheck(expr.arg, env)
        if not isinstance(fn_type, TFun):
            raise TypeError(f"Not a function: {fn_type}")
        if fn_type.arg != arg_type:
            raise TypeError(f"Type mismatch: expected {fn_type.arg}, got {arg_type}")
        return fn_type.ret
    if isinstance(expr, EIf):
        cond_t = typecheck(expr.cond, env)
        if cond_t != TBool(): raise TypeError(f"Condition must be Bool, got {cond_t}")
        then_t = typecheck(expr.then, env)
        else_t = typecheck(expr.els, env)
        if then_t != else_t: raise TypeError(f"Branch type mismatch: {then_t} vs {else_t}")
        return then_t
    if isinstance(expr, EBinOp):
        lt = typecheck(expr.left, env)
        rt = typecheck(expr.right, env)
        if expr.op in ("+", "-", "*", "/"):
            if lt != TInt() or rt != TInt(): raise TypeError(f"Arithmetic on non-Int")
            return TInt()
        if expr.op in ("==", "<", ">"):
            if lt != rt: raise TypeError(f"Comparison type mismatch")
            return TBool()
        if expr.op == "&&" or expr.op == "||":
            if lt != TBool() or rt != TBool(): raise TypeError(f"Logic on non-Bool")
            return TBool()
    if isinstance(expr, ELet):
        val_t = typecheck(expr.val, env)
        return typecheck(expr.body, {**env, expr.name: val_t})
    raise TypeError(f"Unknown expression: {expr}")

def test():
    assert typecheck(EInt(42)) == TInt()
    assert typecheck(EBool(True)) == TBool()
    # Lambda
    inc = ELam("x", TInt(), EBinOp("+", EVar("x"), EInt(1)))
    assert typecheck(inc) == TFun(TInt(), TInt())
    # Application
    assert typecheck(EApp(inc, EInt(5))) == TInt()
    # Type error
    try:
        typecheck(EApp(inc, EBool(True)))
        assert False
    except TypeError:
        pass
    # If
    assert typecheck(EIf(EBool(True), EInt(1), EInt(2))) == TInt()
    try:
        typecheck(EIf(EInt(1), EInt(1), EInt(2)))
        assert False
    except TypeError:
        pass
    # Let
    expr = ELet("x", EInt(5), EBinOp("+", EVar("x"), EInt(3)))
    assert typecheck(expr) == TInt()
    # Higher-order
    apply_fn = ELam("f", TFun(TInt(), TInt()), EApp(EVar("f"), EInt(10)))
    assert typecheck(apply_fn) == TFun(TFun(TInt(), TInt()), TInt())
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: type_check.py test")
