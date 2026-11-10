program CommerceQueueProfile;
var
  queue: report;
  retry_delays: array;
begin
  queue := queue_profile('checkout', 6, 12, 4, true);
  retry_delays := retry_schedule(5, 0.5, 2, 20);
  writeln(queue.max_in_flight);
  writeln(queue.max_attempts);
  writeln(retry_delays);
end.
