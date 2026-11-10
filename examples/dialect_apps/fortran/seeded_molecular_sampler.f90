program SeededMolecularSampler
implicit none
real :: temperature
real :: molecular_mass
real :: samples
temperature = 300 * K
molecular_mass = 6.6335209e-26 * kg
samples = sample_maxwell(temperature, molecular_mass, 12, 7)
print *, count(samples)
print *, mean(samples)
print *, variance(samples)
end program SeededMolecularSampler
