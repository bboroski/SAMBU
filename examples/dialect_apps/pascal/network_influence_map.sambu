program NetworkInfluenceMap;
var
  graph: network;
  metrics: report;
  propagation: report;
begin
  graph := network(["origin", "east", "west", "south"], [["origin", "east"], ["origin", "west"], ["east", "south"], ["west", "south"]]);
  metrics := network_metrics(graph);
  propagation := influence(graph, ["origin"], 3, 0.8);
  writeln(metrics.node_count);
  writeln(metrics.edge_count);
  writeln(propagation.scores);
end.
