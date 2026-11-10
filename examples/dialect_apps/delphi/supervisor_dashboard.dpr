program SupervisorDashboard;
function keep_state(state: real; message: real): real;
begin
  keep_state := state + message;
end;
var
  overseer: supervisor_ref;
  worker: actor_ref;
  status: report;
begin
  overseer := supervisor('one_for_one', 3, 60);
  worker := actor(keep_state, 0, 16);
  supervise(overseer, worker);
  actor_send(worker, 10);
  actor_drain(worker, 1);
  status := supervisor_status(overseer);
  writeln(status.status);
  writeln(status.strategy);
end.
