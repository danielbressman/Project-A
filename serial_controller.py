#!/usr/bin/env python3
# Written by Daniel Bressman

#TODO
#Need to implement this into the Longevity workflow
#add timeout to serial_logcat, might hard code since its hard passing multiple
#args into a pool of serial devices
#Figure out logging/displaying device information to the user, each function has
#access to which device is being ran at any given time. Logcat could display status
#updates with device tag for more specific information

import time
try:
    import serial
except ImportError:
    print('Error importing serial module.')
    print('Please run "pip3 install pyserial"')
from multiprocessing import Pool
from functools import partial
from terminal_commands import store_output
import io

"""
Any command argument called device is expecting a list of USB devices
formatted like:
/dev/ttyUSB0
/dev/ttyUSB1
I use a get devices function to figure this out.
You can also ommit any devices you don't want to receive the command
"""

def get_devices():
    """
    Checks /dev for USB devices and returns a list of the devices found
    /dev/ttyUSB0
    /dev/ttyUSB1
    """
    devices = []
    device_output = store_output(['ls','/dev'])
    for device in device_output:
        if "ttyUSB" in device:
            devices.append('/dev/'+device)
    if not devices:
        print('No Null-Modem cables detected')
    return devices

def run_logcat(device_port):
    """
    Runs logcat on device for set amount of time in seconds
    Currently hard-coded to run for 21600 seconds (6 hours)
    """
    device = serial.Serial(port=device_port,baudrate=115200,timeout=1)
    device.write(b'logcat\n')
    all_output = []
    start_time = time.time()
    while True:
        #Each line from the device
        output = device.readline()
        #Adding it to variable
        all_output.append(output)
        #Printing a line
        #print(output)
        current_time = time.time()
        #Exit condition - test running for 6 hours
        if current_time-start_time > 21600:
            break
    #Stopping logcat on serial device(Same as ctrl+c)
    device.write(b'\x03')
    #Resets buffer to pull device info more reliably
    device.reset_input_buffer()
    device.reset_output_buffer()
    time.sleep(5)
    #Runs wpa_cli on device
    device_info = get_device_status(device_port)
    #Parses wpa_cli output, sorry quick and dirty
    for info in device_info:
        if 'Channel:' in info:
            channel = info[9:]
        elif 'SSID:' in info:
            ssid = info[6:]
        elif 'Inventory ID:' in info:
            inventory_id = info[14:]
        else:
            pass
    #add time?
    with open(inventory_id+'_'+channel+'_'+ssid+'_logcat.log','wb') as logfile:
        for line in all_output:
            logfile.write(line)
    logfile.close()

def run_command(command,device_port,rate):
    """
    Used to run a single command on the devices. Currently this doesn't store any
    output and most likely will need to based on the command ran
    """
    try:
        device = serial.Serial(port=device_port,baudrate=rate,timeout=1)
        #Presses ctrl+c to clear text left by user
        device.write((command+'\n').encode())
        all_output = []
        while True:
            output = device.readline()
            #Adding it to variable
            all_output.append(output)
            #This function assumes that the output isn't infinite.
            if output == b'':
                break
        #Returns device tag so you know where the output came from
        return (decode_output(all_output))
    except serial.serialutil.SerialException:
        print('***Unable to run command on device over serial, verify connection.***')
        print('You can try:')
        print('(1) Run: sudo chmod 766 /dev/ttyUSB*')
        print('(2) Verify no serial windows are left open')
        print('(3) Check to make sure you can access devices over serial\n')
        return False

def start_logcat(devices):
    """
    Starts logcat on serial devices. Pool will need to be handled differently for the
    run_command function since you can't pass multiple arguments in a normal way.
    """
    p = Pool()
    p.map(run_logcat,devices)
    p.close()

def send_command(command,devices):
    """
    Not so sure how this works, just don't touch and enjoy the black magic.
    Also it seems like whatever argument is the iterable needs to be last on
    the function
    run_command(devices,command) is not possible.
    """
    p = Pool()
    func = partial(run_command,command)
    results = p.map(func, devices)
    p.close()
    #Returns ([device_tag, command output])
    return results

def decode_output(output):
    """
    Decodes list of output from device Returns decoded list.
    """
    try:
        decoded = []
        for i in output:
            decoded.append(i.decode().strip('\n\r'))
        return decoded
    except UnicodeDecodeError:
        return ''

"""
I've thrown the following 3 functions in to make it so I can further modify the
logcat name. Need to restructure so these aren't included in main script
"""

def get_device_status(device):
    """
    Checks for various information from DUT using wpa_cli.
    """
    command = 'wpa_cli -i wlan1 status; wpa_cli status\n'
    #Do device status check - This could include devices inventory tag potentially
    output = run_command(command,device)
    #Awkward parsing
    format_output = []
    for line in output[1]:
        if 'address' in line:
            if '_address' in line:
                format_output.append('IP Address: '+line[11:])
            else:
                #Some devices have 2 antennas
                if('MAC Address: '+line[8:]) not in format_output:
                    mac = line[8:]
                    format_output.append('Inventory ID: '+get_device_name(mac))
                    format_output.append('MAC Address: '+mac)
        if 'freq' in line:
            #Need to use freq/channel dictionary to figure out channel
            format_output.append('Channel: '+frequency_to_channel(line[5:]))
        if 'ssid' in line and 'bssid' not in line:
            format_output.append('SSID: '+line[5:])
    if not format_output:
        #Might have some problems naming logcat if the device disconnects during test
        #Maybe should return a default so its not lost?
        print('couldnt get output')
    return format_output

def frequency_to_channel(freq):
    """
    Returns channel based on frequency. This is necessary since wpa_cli only
    shows frequency. Conversion dictionary stored in config file
    """
    freq = int(freq)
    for channel,frequency in CHANNELS.items():
        if frequency == freq:
            return str(channel)

def get_device_name(mac):
    """
    Returns device inventory name based on mac address
    """
    with open('Nest_Devices_10_28_19.csv','r') as csvfile:
        for line in csvfile:
            if mac in line:
                device = line.split(',')
                return device[0]
