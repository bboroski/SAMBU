program PlumageInsulationModel
implicit none
real :: insulation
insulation = plumage_insulation(1.0, 0.2, 0.1)
print *, insulation.effective_index
print *, insulation.retained_fraction
end program PlumageInsulationModel
