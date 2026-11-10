program ActorMessageService;
function accumulate(state: real; message: real): real;
begin
  accumulate := state + message;
end;
var
  worker: actor_ref;
  report: report;
begin
  worker := actor(accumulate, 0, 8);
  actor_send(worker, 5);
  actor_send(worker, 7);
  report := actor_drain(worker, 2);
  writeln(report.processed);
  writeln(actor_state(worker));
end.
