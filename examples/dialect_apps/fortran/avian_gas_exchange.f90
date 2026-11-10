program AvianGasExchange
implicit none
real :: exchange
exchange = avian_gas_exchange(12.0, 0.21, 0.25, 21000 * Pa)
print *, exchange.oxygen_uptake_proxy
print *, exchange.relative_delivery_proxy
end program AvianGasExchange
