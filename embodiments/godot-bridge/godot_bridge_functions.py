import requests
import ast
import random
import logging


def simulation_testing():
    """
    This is to stress the CPU using Godot. You should be able to see the red cube filled with
    small red cubes inside. You can simply uncomment this function in main() to test the
    stress and increase the iteration numbers to stress more..
    """
    array = [[random.randint(0, 64), random.randint(0, 64), random.randint(0, 64)] for _ in
             range(1000)]
    return array


def godot_data(data_input):
    """
    Simply clean the list and remove all unnecessary special characters and deliver with name, xyz
    only
    """
    return ast.literal_eval(data_input)


def feagi_breakdown(data):
    """
    Designed for genome 2.0 only. Data is the input from feagi's raw data.
    This function will detect if cortical area list is different than the first, it will generate
    genome list for godot automatically.
    """
    try:
        new_list = []
        for i in data['godot']:
            new_list.append([i[1], i[2], i[3]])
        return new_list
    except requests.exceptions.RequestException as error:
        logging.exception(error)
        print("Exception during feagi_breakdown", error)
        return []


def convet_godot_coord_to_feagi_coord(stimulation_from_godot, cortical_data_list):
    """
    Convert absolute coordinate from godot to relative coordinate for FEAGI. coordinates are from
    the genome["blueprint"].
    """
    relative_coordinate = {"data": {"direct_stimulation": {}}}
    if stimulation_from_godot:
        for godot_cortical_name, xyz_list in stimulation_from_godot["data"]["direct_stimulation"].items():
            if godot_cortical_name in cortical_data_list:
                if godot_cortical_name not in relative_coordinate["data"]["direct_stimulation"]:
                    relative_coordinate["data"]["direct_stimulation"][godot_cortical_name] = []
                    for xyz in xyz_list:
                        new_xyz = [xyz[0] - cortical_data_list[godot_cortical_name]['coordinates_3d'][0],
                                   xyz[1] - cortical_data_list[godot_cortical_name]['coordinates_3d'][1],
                                   xyz[2] - cortical_data_list[godot_cortical_name]['coordinates_3d'][2]]
                        relative_coordinate["data"]["direct_stimulation"][godot_cortical_name].append(new_xyz)
    return relative_coordinate
