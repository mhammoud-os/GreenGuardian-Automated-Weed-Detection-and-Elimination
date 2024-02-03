add_executable(picoMotorControls
	picoMotorControls.c
        )

# pull in common dependencies
target_link_libraries(picoMotorControls pico_stdlib hardware_pwm hardware_clocks)

# create map/bin/hex file etc.
pico_add_extra_outputs(picoMotorControls)

# add url via pico_set_program_url
example_auto_set_url(picoMotorControls)

pico_enable_stdio_usb(picoMotorControls 1)
pico_enable_stdio_uart(picoMotorControls 0)
