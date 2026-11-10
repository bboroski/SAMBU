program ProbabilityLab;
var
  thermal_state: real;
  occupancy: real;
  uncertainty: real;
begin
  thermal_state := boltzmann(1e-21 * J, 300 * K);
  occupancy := partition([0 * J, 1e-21 * J, 2e-21 * J], 300 * K);
  uncertainty := entropy([0.25, 0.25, 0.25, 0.25]);
  writeln(thermal_state);
  writeln(occupancy);
  writeln(uncertainty);
end.
