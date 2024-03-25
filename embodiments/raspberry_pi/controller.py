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
from time import sleep
import threading
from configuration import *
from feagi_connector import sensors
from feagi_connector import feagi_interface as feagi
from feagi_connector import pns_gateway as pns
from feagi_connector.version import __version__
from feagi_connector import actuators
import raspberry_PI_library as rpi


def action(obtained_data):
    recieve_gpio_data = actuators.get_gpio_data(obtained_data)
    if recieve_gpio_data:
        for i in recieve_gpio_data:
            rpi.power_pin(i)
    else:
        rpi.depower_pin()


if __name__ == "__main__":
    print("Waiting on FEAGI...")

    runtime_data = {
        "current_burst_id": 0,
        "feagi_state": None,
        "cortical_list": (),
        "battery_charge_level": 1,
        "host_network": {},
        'motor_status': {},
        'servo_status': {}
    }

    # # # FEAGI registration # # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - #
    feagi_settings, runtime_data, api_address, feagi_ipu_channel, feagi_opu_channel = \
        feagi.connect_to_feagi(feagi_settings, runtime_data, agent_settings, capabilities,
                               __version__)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    feagi_settings['feagi_burst_speed'] = float(runtime_data["feagi_state"]['burst_duration'])
    threading.Thread(target=pns.feagi_listener, args=(feagi_opu_channel,), daemon=True).start()

    rpi.configured_board_by_config(capabilities) # pass your config setting to this

    while True:
        try:
            message_from_feagi = pns.message_from_feagi
            if message_from_feagi:
                pns.check_genome_status_no_vision(message_from_feagi)
                feagi_settings['feagi_burst_speed'] = \
                    pns.check_refresh_rate(message_from_feagi, feagi_settings['feagi_burst_speed'])
                obtained_signals = pns.obtain_opu_data(message_from_feagi)
                action(obtained_signals)
            generic_input_dict = dict()
            generic_input_dict['i_gpio'] = rpi.gather_all_input_data()
            message_to_feagi = sensors.add_generic_input_to_feagi_data(generic_input_dict, message_to_feagi)
            pns.signals_to_feagi(message_to_feagi, feagi_ipu_channel, agent_settings)
            sleep(feagi_settings['feagi_burst_speed'])
        except KeyboardInterrupt:
            rpi.clear_gpio()
