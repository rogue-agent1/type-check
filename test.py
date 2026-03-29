from type_check import typed, check_type, Struct
@typed
def add(a: int, b: int) -> int: return a + b
assert add(1, 2) == 3
try: add("x", 2); assert False
except TypeError: pass
check_type("hello", str, "test")
try: check_type(123, str, "test"); assert False
except TypeError: pass
print("Type check tests passed")