program ExperimentAnalyser;
var
  experiment: report;
begin
  experiment := ab_test(1000, 120, 1000, 136);
  writeln(experiment.absolute_lift);
  writeln(experiment.z_score);
  writeln(experiment.p_value);
end.
