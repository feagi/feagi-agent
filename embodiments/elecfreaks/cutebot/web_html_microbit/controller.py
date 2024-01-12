#!/usr/bin/env python
"""
Copyright 2016-2023 The FEAGI Authors. All Rights Reserved.
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

import asyncio
import threading
from collections import deque
from datetime import datetime
from time import sleep
import requests
import traceback
import websockets
from configuration import *
from version import __version__
from feagi_agent import pns_gateway as pns
from feagi_agent import sensors as sensors
from feagi_agent import feagi_interface as feagi

ws = deque()
ws_operation = deque()
previous_data = ""


async def bridge_to_godot():
    while True:
        if ws:
            try:
                if ws_operation:
                    if len(ws) > 0:
                        if len(ws) > 2:
                            stored_value = ws.pop()
                            ws.clear()
                            ws.append(stored_value)
                    await ws_operation[0].send(str(ws[0]))
                    ws.pop()
                if "stimulation_period" in runtime_data:
                    sleep(runtime_data["stimulation_period"])
            except Exception as error:
                print("error: ", error)
                sleep(0.001)
        else:
            sleep(0.001)


def bridge_operation():
    asyncio.run(bridge_to_godot())


async def echo(websocket):
    """
    The function echoes the data it receives from other connected websockets
    and sends the data from FEAGI to the connected websockets.
    """
    async for message in websocket:
        if not ws_operation:
            ws_operation.append(websocket)
        else:
            ws_operation[0] = websocket
        ir_list = []
        if message[0] == 'f':
            pass
        else:
            ir_list.append(0)
        if message[1] == 'f':
            pass
        else:
            ir_list.append(1)
        try:
            x_acc = int(message[2:6]) - 1000
            y_acc = int(message[6:10]) - 1000
            z_acc = int(message[10:14]) - 1000
            ultrasonic = float(message[14:16])
            sound_level = int(message[16:18])
            # Store values in dictionary
            microbit_data['ir'] = ir_list
            microbit_data['ultrasonic'] = ultrasonic / 25
            microbit_data['accelerator'] = {"0": x_acc, "1": y_acc, "2": z_acc}
            microbit_data['sound_level'] = {sound_level}
        except Exception as Error_case:
            pass
            # print("error: ", Error_case)
            # print("raw: ", message)


async def main():
    """
    The main function handles the websocket and spins the asyncio to run the echo function
    infinitely until it exits. Once it exits, the function will resume to the next new websocket.
    """
    async with websockets.serve(echo, agent_settings["godot_websocket_ip"],
                                agent_settings['godot_websocket_port']):
        await asyncio.Future()  # run forever


def websocket_operation():
    """
    WebSocket initialized to call the echo function using asyncio.
    """
    asyncio.run(main())


def action(obtained_data):
    WS_STRING = ""
    if 'motor_percentage' in obtained_data:
        if obtained_data['motor_percentage']:
            WS_STRING = ""
            if len(obtained_data['motor_percentage']) >= 3:
                if 0 in obtained_data['motor_percentage']:
                    if 1 in obtained_data['motor_percentage']:
                        if obtained_data['motor_percentage'][0] >= obtained_data['motor_percentage'][1]:
                            obtained_data['motor_percentage'].pop(1)
                        else:
                            obtained_data['motor_percentage'].pop(0)
                if 2 in obtained_data['motor_percentage']:
                    if 3 in obtained_data['motor_percentage']:
                        if obtained_data['motor_percentage'][2] >= obtained_data['motor_percentage'][3]:
                            obtained_data['motor_percentage'].pop(3)
                        else:
                            obtained_data['motor_percentage'].pop(2)
            new_dict = {'motor': {}}
            for x in obtained_data['motor_percentage']:
                if x in [0, 1, 2, 3]:
                    new_dict['motor'][x] = obtained_data['motor_percentage'][x]
            for i in sorted(new_dict['motor']):  # Ensure that it's in order for microbit
                if i in [0, 1]:
                    data_power = new_dict['motor'][i]
                    if data_power <= 0:
                        data_power = 1
                    WS_STRING += str(i) + str(data_power-1).zfill(2)  # Append the motor data as a two-digit
                    # string
                elif i in [2, 3]:
                    data_power = new_dict['motor'][i]
                    if data_power <= 0:
                        data_power = 1
                    WS_STRING += str(i) + str(data_power-1).zfill(2)  # Append the motor data as a two-digit
                    # string
                else:
                    WS_STRING += str(i) + "00"  # If the motor value is not present, append "00"
    if 'motor_position' in obtained_data:
        if obtained_data['motor_position']:
            WS_STRING = ""
            if len(obtained_data['motor_position']) >= 3:
                if 0 in obtained_data['motor_position']:
                    if 1 in obtained_data['motor_position']:
                        if obtained_data['motor_position'][0] >= obtained_data['motor_position'][1]:
                            obtained_data['motor_position'].pop(1)
                        else:
                            obtained_data['motor_position'].pop(0)
                if 2 in obtained_data['motor_position']:
                    if 3 in obtained_data['motor_position']:
                        if obtained_data['motor_position'][2] >= obtained_data['motor_position'][3]:
                            obtained_data['motor_position'].pop(3)
                        else:
                            obtained_data['motor_position'].pop(2)
            new_dict = {'motor': {}}
            for x in obtained_data['motor_position']:
                if x in [0, 1, 2, 3]:
                    new_dict['motor'][x] = obtained_data['motor_position'][x]
            for i in sorted(
                    new_dict['motor']):  # Ensure that it's in order for microbit
                if i in [0, 1]:
                    data_power = new_dict['motor'][i]
                    if data_power <= 0:
                        data_power = 1
                    WS_STRING += str(i) + str(data_power * 10).zfill(2)  # Append the motor
                    # data as a two-digit string
                elif i in [2, 3]:
                    data_power = new_dict['motor'][i]
                    if data_power <= 0:
                        data_power = 1
                    WS_STRING += str(i) + str(data_power * 10).zfill(2)  # Append the motor data
                    # as a two-digit  string
                else:
                    WS_STRING += str(
                        i) + "00"  # If the motor value is not present, append "00"
    print("HERE: ", WS_STRING)
    if WS_STRING != "":
        if len(WS_STRING) != 6:
            if int(WS_STRING[0]) < 2:
                WS_STRING = WS_STRING + "500"
            else:
                WS_STRING = "500" + WS_STRING
        WS_STRING = WS_STRING + "#"
        ws.append(WS_STRING)


if __name__ == "__main__":
    CHECKPOINT_TOTAL = 5
    FLAG_COUNTER = 0
    microbit_data = {'ir': [], 'ultrasonic': {}, 'accelerator': {}, 'sound_level': {}}
    threading.Thread(target=websocket_operation, daemon=True).start()
    # threading.Thread(target=bridge_to_godot, daemon=True).start()
    threading.Thread(target=bridge_operation, daemon=True).start()
    feagi_flag = False
    print("Waiting on FEAGI...")
    while not feagi_flag:
        feagi_flag = feagi.is_FEAGI_reachable(
            os.environ.get('FEAGI_HOST_INTERNAL', "127.0.0.1"),
            int(os.environ.get('FEAGI_OPU_PORT', "3000"))
        )
        sleep(2)
    previous_data_frame = {}
    runtime_data = {"cortical_data": {}, "current_burst_id": None,
                    "stimulation_period": 0.01, "feagi_state": None,
                    "feagi_network": None}

    feagi_auth_url = feagi_settings.pop('feagi_auth_url', None)
    print("FEAGI AUTH URL ------- ", feagi_auth_url)

    # # # FEAGI registration # # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - #
    feagi_settings, runtime_data, api_address, feagi_ipu_channel, feagi_opu_channel = \
        feagi.connect_to_feagi(feagi_settings, runtime_data, agent_settings, capabilities,
                               __version__)
    threading.Thread(target=pns.feagi_listener, args=(feagi_opu_channel,), daemon=True).start()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    msg_counter = runtime_data["feagi_state"]['burst_counter']
    runtime_data['accelerator'] = {}
    while True:
        try:
            message_from_feagi = pns.message_from_feagi
            # OPU section STARTS
            if message_from_feagi:
                obtained_signals = pns.obtain_opu_data(message_from_feagi)
                action(obtained_signals)
            # OPU section ENDS
            message_to_feagi = sensors.add_ultrasonic_to_feagi_data(microbit_data['ultrasonic'], message_to_feagi)
            message_to_feagi = sensors.add_infrared_to_feagi_data(microbit_data['ir'],
                                                                  message_to_feagi,
                                                                  capabilities)
            message_to_feagi = sensors.add_acc_to_feagi_data(microbit_data['accelerator'], message_to_feagi)
            message_to_feagi['timestamp'] = datetime.now()
            message_to_feagi['counter'] = msg_counter
            sleep(feagi_settings['feagi_burst_speed'])
            pns.signals_to_feagi(message_to_feagi, feagi_ipu_channel, agent_settings)
            message_to_feagi.clear()
        except Exception as e:
            print("ERROR: ", e)
            traceback.print_exc()
            break
