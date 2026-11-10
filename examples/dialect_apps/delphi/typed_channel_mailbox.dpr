program TypedChannelMailbox;
var
  mailbox: channel_ref;
  accepted: real;
  received: real;
begin
  mailbox := channel('float', 4);
  accepted := channel_send(mailbox, 42);
  channel_send(mailbox, 84);
  received := channel_receive(mailbox);
  writeln(accepted);
  writeln(received);
end.
