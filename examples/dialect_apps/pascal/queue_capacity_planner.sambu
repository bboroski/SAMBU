program QueueCapacityPlanner;
var
  queue: report;
  delays: array;
begin
  queue := queue_profile('orders', 4, 8, 3, true);
  delays := retry_schedule(4, 1, 2, 30);
  writeln(queue.max_in_flight);
  writeln(queue.dead_letter_queue);
  writeln(delays);
end.
