program WeeklySessionPlanner;
var
  plan: report;
begin
  plan := weekly_schedule([["Monday", "09:00", "Systems Review", 12], ["Wednesday", "14:30", "Scientific Lab", 16], ["Friday", "11:00", "Release Clinic", 8]]);
  writeln(plan.session_count);
  writeln(plan.active_weekdays);
end.
