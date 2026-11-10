program ConversionFunnelConsole;
var
  funnel_report: report;
begin
  funnel_report := funnel([10000, 6200, 1800, 900]);
  writeln(funnel_report.overall_conversion);
  writeln(funnel_report.step_conversion);
  writeln(funnel_report.total_lost);
end.
