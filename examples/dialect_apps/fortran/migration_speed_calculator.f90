program MigrationSpeedCalculator
implicit none
real :: distance
real :: duration
real :: speed
distance = 850 * km
duration = 10 * 3600 * s
speed = migration_speed(distance, duration)
print *, speed
end program MigrationSpeedCalculator
