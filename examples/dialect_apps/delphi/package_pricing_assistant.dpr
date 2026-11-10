program PackagePricingAssistant;
var
  offer: report;
begin
  offer := package_pricing(120, 600, 6);
  writeln(offer.effective_session_price);
  writeln(offer.savings);
  writeln(offer.discount_rate);
end.
