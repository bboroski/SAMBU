program AudioSessionBrief;
var
  mix: report;
begin
  mix := audio_profile('Harlem Session', 93, 60, 15, -0.3, true, true, true, true, true);
  writeln(mix.bpm);
  writeln(mix.swing_percent);
  writeln(mix.mix_ceiling_is_below_full_scale);
end.
