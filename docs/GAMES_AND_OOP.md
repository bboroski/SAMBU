# SAMBU 0.6.0 — object model and game rules

## Object-oriented language slice

SAMBU 0.6.0 introduces an executable first OOP foundation:

- class declarations;
- object construction by calling the class;
- an optional constructor method named init;
- mutable public instance fields;
- instance methods with explicit self as their first parameter;
- single inheritance with inherited constructors/methods and method overriding;
- runtime checks for constructor/method arity and invalid base classes.

Example:

~~~sambu
class Animal {
  fn init(self, name) { self.name = name }
  fn speak(self) { return self.name + " makes a sound" }
}

class Dog extends Animal {
  fn speak(self) { return self.name + " barks" }
}

let pet = Dog("Rex")
print(pet.speak())
~~~

Fields are currently public and dynamically created. A method must declare self first. If init is not present, construction accepts no arguments. Inherited methods are found through the base-class chain; a subclass method with the same name overrides the base method.

### Deliberate OOP boundaries

This is a working object model, not yet a complete statically typed enterprise OOP system. Interfaces/protocols, traits/mixins, multiple inheritance, access modifiers, static/class methods, properties, operator overloading, generic types, abstract classes, explicit super dispatch and compile-time override/type checks are not implemented. Local let bindings remain immutable; object fields are mutable. Composition is available by storing one object in another object's field.

The object runtime remains inside the existing interpreter and uses Python's managed memory. SAMBU does not claim deterministic destruction, Rust-like ownership guarantees or a native object ABI.

## Rock-paper-scissors

~~~sambu
let result = rps_round("rock", "scissors")
print(result.outcome) # win, loss, or draw
print(result.winner)  # player, opponent, or null
~~~

Moves are case-insensitive strings: rock, paper or scissors. The function is deterministic and has no random or network behavior.

## Tic-tac-toe

The board is a flat nine-cell array in row-major order. Cells are "X", "O", "." or null/empty string for an empty cell. X starts.

~~~sambu
let board0 = [".", ".", ".", ".", ".", ".", ".", ".", "."]
let board1 = tic_tac_toe_move(board0, "X", 0)
let board2 = tic_tac_toe_move(board1.board, "O", 4)
print(tic_tac_toe_state(board2.board).next_player)
~~~

- tic_tac_toe_state(board) validates reachability and reports status, winner, next_player and moves_remaining.
- tic_tac_toe_move(board, player, position) returns a new state record; it does not mutate the input array.
- Positions are zero-based from 0 through 8.
- The engine rejects unreachable boards, moves by the wrong player, occupied cells and moves after the game ends.

The legal-board validator enumerates the finite set of reachable game states and stops expanding a state immediately after a win.


## Passage curtain: occupancy-aware state pattern

The [passage curtain example](../examples/passage_curtain.sambu) models an automatic curtain or door at a passage:

- The first confirmed arrival changes the state from closed to open.
- Further arrivals keep it open and increase the occupancy count.
- An exit reduces the count; the curtain closes only after the last occupant leaves.
- Extra exit events never make the count negative.

This is a host-neutral state model, not a renderer, sensor driver or animation system. A game engine, PLC or desktop host must supply trustworthy entry/exit events, debounce noisy sensors, animate the physical curtain, and provide a manual/emergency override. In a real installation, closing must be inhibited whenever occupancy is uncertain or a safety sensor reports an obstruction.

## Next OOP milestones

1. Add a shared semantic type model for class names, instance fields, method signatures and inheritance.
2. Add interfaces/protocols and explicit visibility/access control.
3. Add parent-method dispatch and static members with deterministic lookup rules.
4. Add class-aware diagnostics and completion from typed AST and symbol scopes.
5. Add serialization rules only when object graph identity, cycles and compatibility are specified.
