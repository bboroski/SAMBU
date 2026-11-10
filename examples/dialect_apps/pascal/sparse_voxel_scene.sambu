program SparseVoxelScene;
var
  world: grid;
  mesh: report;
  portable: text;
begin
  world := voxel_grid(8, 1000);
  voxel_set(world, 0, 0, 0, 2);
  voxel_set(world, 1, 0, 0, 2);
  voxel_set(world, 1, 1, 0, 3);
  mesh := voxel_mesh(world);
  portable := voxel_export(world, 'generic');
  writeln(voxel_count(world));
  writeln(mesh.triangle_count);
  writeln(portable != '');
end.
