"""
Copyright 2016-2022 The FEAGI Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================
"""
import RPi.GPIO as GPIO

# Dictionary to keep track of GPIO modes
gpio_modes = {}


# Function to setup GPIO
def setup_gpio(pin, mode):
    global gpio_modes
    GPIO.setup(pin, mode)
    gpio_modes[pin] = mode


def depower_pin():
    global gpio_modes
    for pin in gpio_modes:
        if gpio_modes[pin] == 0:
            GPIO.output(pin, GPIO.LOW)


def power_pin(pin):
    global gpio_modes
    if pin in gpio_modes:
        if gpio_modes[pin] == 0:
            GPIO.output(pin, GPIO.HIGH)


def read_pin(pin):
    global gpio_modes
    if pin in gpio_modes:
        if gpio_modes[pin] == 1:
            return GPIO.input(pin)


def gather_all_input_data():
    global gpio_modes
    input_list = dict()
    for pin in gpio_modes:
        if gpio_modes[pin] == 1:
            data = read_pin(pin)
            if data:
                location_string = str(pin) + "-0-0"
                input_list[location_string] = 100
    return input_list


def get_available_gpios():
    available_gpios = []
    for pin in range(2, 28):  # The latest Raspberry Pi, the Raspberry Pi 5, features 28 GPIO pins.
        try:
            # GPIO.setup(pin, GPIO.IN)
            setup_gpio(pin, GPIO.OUT)
            available_gpios.append(pin)
            # GPIO.cleanup(pin)
        except ValueError:
            pass
    return available_gpios


# Function to check GPIO mode
def check_gpio_mode(pin):
    global gpio_modes
    if pin in gpio_modes:
        return "Output" if gpio_modes[pin] == GPIO.OUT else "Input"
    else:
        return "Not configured"


def configured_board_by_config(capabilities):
    if 'GPIO' in capabilities:
        if 'port' in capabilities['GPIO']:
            for pin in capabilities['GPIO']['port']:
                GPIO.setup(int(pin), capabilities['GPIO']['port'][pin])
                gpio_modes[int(pin)] = capabilities['GPIO']['port'][pin]
    print(gpio_modes)


def clear_gpio():
    GPIO.cleanup()


GPIO.setmode(GPIO.BCM)  # Using Broadcom pin numbering
# gpios = get_available_gpios()
# print(gpio_modes)
# GPIO.cleanup()
