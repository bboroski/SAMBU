# Object-oriented programming

SAMBU's interpreter includes an object-oriented programming slice. The object model is part of the interpreted language; it is distinct from the Python classes used by host-side SAMBU modules.

## Core concepts

The repository's OOP documentation and typed AST describe support for:

- class declarations;
- object construction by calling a class;
- optional `init` constructors;
- instance fields and methods;
- single class inheritance;
- method overriding;
- interfaces;
- traits;
- abstract and final class/method declarations;
- method visibility;
- static fields and methods;
- explicit parent-method dispatch through `super`.

The exact maturity of each feature is alpha-level and should be verified against the parser, runtime and tests before relying on it in a critical system.

## Basic example

```sambu
class Animal {
  fn init(self, name) {
    self.name = name
  }

  fn speak(self) {
    return self.name + " makes a sound"
  }
}

class Dog extends Animal {
  fn speak(self) {
    return self.name + " barks"
  }
}

let pet = Dog("Rex")
print(pet.speak())
```

Methods use an explicit `self` parameter. A subclass can override an inherited method.

## Interfaces and traits

The extended object model includes interface contracts and reusable trait methods.

```sambu
interface Renderable {
  fn render(self)
}

trait Identified {
  fn identity(self) {
    return self.name
  }
}

class Button implements Renderable uses Identified {
  fn init(self, name) {
    self.name = name
  }

  fn render(self) {
    return "[" + self.identity() + "]"
  }
}

let save = Button("Save")
print(save.render())
```

Interfaces describe required method names and arities. Traits provide reusable method implementations. A conflict between trait methods must be handled explicitly by the class implementation.

## Static, abstract and final members

The extended syntax supports static members and abstract/final declarations. Their purpose is to represent class-level state and explicit inheritance constraints. Consult the implementation and executable examples for exact validation rules.

## Design boundaries

SAMBU remains an interpreted alpha language. It should not be described as having:
- a native object ABI;
- Rust-style ownership or borrow checking;
- deterministic object destruction;
- multiple inheritance unless the current implementation explicitly adds it;
- complete compile-time type checking.

The runtime uses Python-managed memory. `let` bindings and object-field mutation have different semantics: a binding can be immutable while fields on an object remain mutable.

## Game-state helpers

The language includes deterministic game helpers:

```sambu
let result = rps_round("rock", "scissors")
print(result.outcome)

let empty = [".", ".", ".", ".", ".", ".", ".", ".", "."]
let after_x = tic_tac_toe_move(empty, "X", 0)
let after_o = tic_tac_toe_move(after_x.board, "O", 4)
print(tic_tac_toe_state(after_o.board).next_player)
```

Tic-tac-toe uses a flat row-major nine-cell board, zero-based positions, and X as the first player. The functions validate reachable game states and reject illegal moves.

## Related pages

- [Syntax and control flow](SYNTAX-AND-CONTROL-FLOW.md)
- [Domain libraries](DOMAIN-LIBRARIES.md)
- [Language tour](LANGUAGE-TOUR.md)
