program SparseVoxelSpectrum
implicit none
real :: world
real :: spectrum
world = voxel_grid(8, 1000)
voxel_set(world, 0, 0, 0, 1)
voxel_set(world, 1, 0, 0, 1)
voxel_set(world, 1, 1, 0, 2)
spectrum = voxel_spectral_profile(world)
print *, spectrum.vertex_count
print *, spectrum.edge_count
print *, spectrum.connected_components
end program SparseVoxelSpectrum
