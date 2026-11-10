program MaxwellSpeedProfile
implicit none
real :: temperature
real :: molecular_mass
real :: profile
temperature = 300 * K
molecular_mass = 6.6335209e-26 * kg
profile = maxwell(temperature, molecular_mass)
print *, profile.most_probable
print *, profile.mean
print *, profile.rms
end program MaxwellSpeedProfile
