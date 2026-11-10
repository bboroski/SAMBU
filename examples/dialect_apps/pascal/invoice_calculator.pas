program InvoiceCalculator;
var
  subtotal: real;
  discount_rate: real;
begin
  subtotal := 240;
  discount_rate := 12.5;
  writeln(reduce_by_percent(subtotal, discount_rate));
  writeln(percent_of(subtotal, discount_rate));
end.
