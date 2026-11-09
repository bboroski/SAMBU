# Syntax and control flow

This page summarizes the documented SAMBU source grammar. It is not a complete formal grammar; consult the parser implementation for exact accepted productions.

## Statements

A program is a sequence of statements separated by newlines or semicolons. Comments begin with `#`.

```sambu
# immutable binding
let reference_temperature = 300 * K

# function declaration
fn square(x) {
  return x * x
}

print(square(12))
```

## Bindings and scopes

- `let name = expression` creates a binding.
- A binding created with `let` is immutable within its scope.
- Redefining a name in the same scope is an error.
- Nested blocks and functions create child lexical scopes.
- A local name may shadow a name from an outer scope where the runtime permits it.
- Built-in units and constants are predeclared and protected against top-level redefinition.

Object fields have separate mutation rules; immutability of a `let` binding does not imply that every object reachable from it is immutable.

## Functions

```sambu
fn square(x) {
  return x * x
}

fn mean_pair(a, b) {
  return (a + b) / 2
}

print(square(7))
print(mean_pair(10, 14))
```

Functions use lexical scope and can return values. Their exact validation and runtime behavior are defined by the interpreter.

## Conditions

```sambu
if (temperature > 300 * K) {
  print("above reference temperature")
} else {
  print("at or below reference temperature")
}
```

SAMBU supports `if` and optional `else`. Conditions follow the interpreter's boolean/truthiness rules.

## Bounded iteration

```sambu
for index in range(5) {
  print(index)
}

for value in [2, 4, 6] {
  print(value)
}
```

The documented `range` forms are:

- `range(stop)`
- `range(start, stop)`
- `range(start, stop, step)`

The current documented safety ceiling is 100,000 values for range generation and 100,000 processed items per `for` loop.

## Expressions and operators

Supported expression forms include literals, names, unary expressions, binary expressions, arrays, function calls, indexing and record-field access.

Documented operator precedence, highest to lowest:

1. Function calls, indexing and field access
2. Unary `-`, `+`, `!`
3. `^` / `**` (right associative)
4. `*`, `/`
5. `+`, `-`
6. `<`, `<=`, `>`, `>=`
7. `==`, `!=`
8. `&&` / `and`
9. `||` / `or`

The exact operator spellings accepted by the current parser take precedence over this summary if a historical guide and source code differ.

## Percentage syntax

SAMBU distinguishes a postfix percentage literal from modulo by whitespace:

```sambu
let discount = 15%
print(discount)    # 0.15
print(10 % 3)      # 1
```

An attached percent sign converts percentage points to a dimensionless ratio. The infix modulo operator requires the separated form. Percentage literals cannot be applied to dimensioned physical quantities.

## Current language boundaries

The historical language guide documents no general `while`, `break`, `continue`, source-level imports, arbitrary Python evaluation, file I/O or network access in the interpreter. Do not assume these features exist without confirming current implementation and tests.

## Related pages

- [Types, units and numerics](TYPES-UNITS-AND-NUMERICS.md)
- [Object-oriented programming](OBJECT-ORIENTED-PROGRAMMING.md)
- [Testing and diagnostics](TESTING-AND-DIAGNOSTICS.md)
