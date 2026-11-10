program BoltzmannOccupancy
implicit none
real :: energy_gap
real :: temperature
real :: probability
energy_gap = 1e-21 * J
temperature = 300 * K
probability = boltzmann(energy_gap, temperature)
print *, probability
end program BoltzmannOccupancy
