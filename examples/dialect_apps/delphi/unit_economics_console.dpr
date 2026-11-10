program UnitEconomicsConsole;
var
  economics: report;
begin
  economics := unit_economics(120, 32, 18);
  writeln(economics.contribution_before_acquisition);
  writeln(economics.contribution_after_acquisition);
  writeln(economics.margin_after_acquisition);
end.
