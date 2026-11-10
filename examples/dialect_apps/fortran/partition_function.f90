program PartitionFunction
implicit none
real :: temperature
real :: partition_sum
temperature = 300 * K
partition_sum = partition([0 * J, 1e-21 * J, 2e-21 * J], temperature)
print *, partition_sum
end program PartitionFunction
