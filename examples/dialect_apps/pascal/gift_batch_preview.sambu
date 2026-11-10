program GiftBatchPreview;
var
  preview: report;
begin
  preview := gift_batch([["g-100", "mira", "oren", 12], ["g-101", "oren", "kai", 4]], [["mira", 80], ["oren", 20], ["kai", 5]]);
  writeln(preview.valid);
  writeln(preview.total_gifted);
  writeln(preview.transaction_count);
end.
