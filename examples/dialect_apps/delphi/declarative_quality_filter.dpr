program DeclarativeQualityFilter;
var
  states: array;
  rule: report;
  result: report;
begin
  states := ['approved', 'pending', 'approved', 'rejected'];
  rule := coq_rule('$', 'eq', 'approved');
  result := coq_filter(states, [rule]);
  writeln(result.matched_count);
  writeln(result.rejected_count);
  writeln(result.items);
end.
