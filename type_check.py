#!/usr/bin/env python3
"""type_check - Runtime type checker with generics, unions, and optionals."""
import sys

class Type:
    pass

class Prim(Type):
    def __init__(self, name): self.name = name
    def check(self, val):
        return {"int": int, "float": (int, float), "str": str, "bool": bool, "none": type(None)}[self.name].__instancecheck__(val) if self.name != "float" else isinstance(val, (int, float))
    def __repr__(self): return self.name

class ListOf(Type):
    def __init__(self, inner): self.inner = inner
    def check(self, val): return isinstance(val, list) and all(self.inner.check(v) for v in val)
    def __repr__(self): return f"List[{self.inner}]"

class DictOf(Type):
    def __init__(self, kt, vt): self.kt, self.vt = kt, vt
    def check(self, val): return isinstance(val, dict) and all(self.kt.check(k) and self.vt.check(v) for k, v in val.items())

class Union(Type):
    def __init__(self, *types): self.types = types
    def check(self, val): return any(t.check(val) for t in self.types)

class Optional(Union):
    def __init__(self, inner): super().__init__(inner, Prim("none"))

class Struct(Type):
    def __init__(self, fields): self.fields = fields  # {name: Type}
    def check(self, val):
        if not isinstance(val, dict): return False
        for name, typ in self.fields.items():
            if name not in val: return False
            if not typ.check(val[name]): return False
        return True

INT, STR, FLOAT, BOOL = Prim("int"), Prim("str"), Prim("float"), Prim("bool")

def test():
    assert INT.check(42)
    assert not INT.check("hi")
    assert FLOAT.check(3.14)
    assert FLOAT.check(3)
    assert ListOf(INT).check([1, 2, 3])
    assert not ListOf(INT).check([1, "x"])
    assert DictOf(STR, INT).check({"a": 1})
    assert not DictOf(STR, INT).check({1: 1})
    assert Union(INT, STR).check(42)
    assert Union(INT, STR).check("hi")
    assert not Union(INT, STR).check([])
    assert Optional(STR).check(None)
    assert Optional(STR).check("ok")
    user = Struct({"name": STR, "age": INT, "tags": ListOf(STR)})
    assert user.check({"name": "Alice", "age": 30, "tags": ["admin"]})
    assert not user.check({"name": "Bob"})
    print("type_check: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: type_check.py --test")
