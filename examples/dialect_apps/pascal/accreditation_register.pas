program AccreditationRegister;
var
  credential: report;
  status: report;
begin
  credential := accreditation_record('SAMBU Maintainer', 'SAMBU-CORE-1', 'Internal Review Board', '2026-01-01', '2027-01-01', ['audit-2026-01', 'test-run-2026-02'], true);
  status := accreditation_status(credential, '2026-11-10');
  writeln(status.status);
  writeln(status.active);
end.
