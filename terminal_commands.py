#!/usr/bin/env python3
# Written by Daniel Bressman

import subprocess

#Runs linux command, decodes and returns output in list
def store_output(command_list, timeout=None):
    try:
        if timeout:
            x = subprocess.check_output(command_list, shell=True, timeout=timeout)
        else:
            x = subprocess.check_output(command_list, shell=True)
        x = decode_output(x.splitlines())
        return x
    except subprocess.TimeoutExpired:
        return False

#Decodes command output
def decode_output(output_list):
    decoded = []
    for output in output_list:
        decoded.append(output.decode('ISO-8859-15'))
    return decoded

#added timeout to this for rvr
def run_command(command):
    try:
        x = subprocess.call(command, timeout=5)
        return x
    except subprocess.TimeoutExpired:
        return 1



