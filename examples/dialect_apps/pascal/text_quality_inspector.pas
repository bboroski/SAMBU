program TextQualityInspector;
var
  profile: report;
  rhythm: report;
begin
  profile := text_profile('Clear language makes a reliable system easier to inspect and maintain.');
  rhythm := prosody_profile('Measured motion carries meaning.\nCareful patterns keep the signal clean.');
  writeln(profile.word_count);
  writeln(profile.lexical_diversity);
  writeln(rhythm.rhyme_density);
end.
