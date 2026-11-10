program GradebookReport;
var
  marks: array;
  average_mark: real;
  sample_spread: real;
begin
  marks := [88, 91, 79, 95, 84];
  average_mark := mean(marks);
  sample_spread := variance(marks);
  writeln(average_mark);
  writeln(sample_spread);
  if average_mark >= 85 then begin
    writeln('honours track');
  end else begin
    writeln('standard review');
  end;
end.
