# Percentage arithmetic

SAMBU 0.10 adds explicit percentage syntax and checked standard-library helpers.

## Literal syntax

A percent sign attached directly to an expression converts percentage points into a dimensionless ratio:

~~~sambu
let discount = 15%
let retained = 100% - discount
print(discount)  # 0.15
print(retained)  # 0.85
~~~

Whitespace is significant. The infix operator in 10 % 3 is modulo and evaluates to 1; the attached postfix token in 10% is a ratio equal to 0.1.

Percentage literals are dimensionless. Applying the percent operator to a physical quantity is rejected.

## Standard library

| Function | Meaning |
|---|---|
| percent_of(amount, rate) | amount multiplied by rate divided by 100 |
| apply_percent(amount, rate) | Apply a signed increase or decrease |
| reduce_by_percent(amount, rate) | Reduce by a rate from 0 through 100 |
| percentage(part, whole) | Return part divided by whole multiplied by 100 |
| percent_change(old, new) | Signed relative change; zero-to-zero returns 0 |
| percent_to_ratio(rate) | Convert percentage points to a ratio |
| ratio_to_percent(ratio) | Convert a ratio to percentage points |
| percentage_points(current, reference) | Difference between two percentage rates |
| clamp_percent(value, min, max) | Clamp a rate to an explicit interval |

All inputs must be finite and dimensionless. A dimensional quantity, boolean, non-finite number, or invalid denominator is rejected instead of silently coerced. percent_change(0, nonzero) is undefined and raises ZeroDivisionError.

## Example

~~~sambu
let base_price = 240
let discount = 12.5%
let savings = percent_of(base_price, ratio_to_percent(discount))
let final_price = base_price - savings
print(savings)
print(final_price)
~~~
