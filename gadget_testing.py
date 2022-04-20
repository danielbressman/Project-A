#!/usr/bin/python3

# written by Daniel Bressman

import subprocess
import sys
import threading
from time import sleep
import serial

red = lambda s: "\033[91m{}\033[00m".format(s)
yellow = lambda s: "\033[93m{}\033[00m".format(s)
prefix = "adb shell am broadcast -a com.amazon.amatest.{}"


class SerialPort:
    def __init__(self, device, baud, timeout=1, rtscts=False):
        self.port = serial.Serial(device, baudrate=baud, timeout=timeout, rtscts=rtscts)

    def write_cmd(self, cmd):
        self.port.write("{}\r\n".format(cmd).encode())
        sleep(0.5)


def port_list(number_devices):
    ports = []
    for i in range(number_devices):
        port = SerialPort("/dev/ttyACM{}".format(i), 115200)
        ports.append(port)
    return ports


def connect_accessory(number_of_devices):
    for device_id in range(1, number_of_devices + 1):
        print(yellow(f"Connecting device ID {device_id}"))
        run_command(prefix.format(f"CONNECT_ACCESSORY --ei id {device_id}"))
        sleep(5)
    print(yellow(f"Connected to {number_of_devices} device IDs"))
    return


def run_uploader_serial(number_of_devices, iterations):
    for iteration in range(1, iterations + 1):
        subprocess.call("adb shell logcat -c", shell=True)
        print(yellow(f"Starting iteration {iteration}"))
        for device_id in range(1, number_of_devices + 1):
            print(yellow(f"Starting uploader on device id={device_id}"))
            run_command(prefix.format(f"START_TEST_BULKCLIENT --ei id {device_id} --ei category 11"))
            if device_id <= number_of_devices:
                command = "adb shell logcat"
                string_to_look_for = "AMABulkDataClient_CompleteTransfer(): Complete bulk data transfer"
                p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
                if not p.stdout:
                    print(red("Failed to pipe stdout of command: " + " ".join(command)))
                    sys.exit()
                while True:
                    line_bytes = p.stdout.readline()
                    line = line_bytes.decode('ISO-8859-15').strip()
                    if string_to_look_for in line:
                        sleep(1.5)
                        break
        else:
            print(red("Error iteration {}".format(iteration)))
            pass

    print(yellow(f"Uploader to {number_of_devices} device(s) completed {iterations} iteration(s)"))
    return


def handle_uploader_concurrent(device_id, iterations, number_of_devices):
    for iteration in range(1, iterations + 1):
        subprocess.call("adb shell logcat -c", shell=True)
        counter = 0
        print(yellow(f"Starting uploader on device ID: {device_id} Iteration: {iteration}"))
        run_command(prefix.format(f"START_TEST_BULKCLIENT --ei id {device_id} --ei category 11"))
        command = "adb shell logcat"
        string_to_look_for = "AMABulkDataClient_CompleteTransfer(): Complete bulk data transfer"
        p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
        if not p.stdout:
            print(red("Failed to pipe stdout of command: " + " ".join(command)))
            sys.exit()
        while True:
            line_bytes = p.stdout.readline()
            line = line_bytes.decode('ISO-8859-15').strip()
            if string_to_look_for in line:
                counter += 1
                if int(counter) >= number_of_devices:
                    sleep(2)
                    print(yellow(f"Uploader completed on ID{device_id} for iteration {iteration}"))
                    break


def run_uploader_concurrent(number_of_devices, iterations):
    threads = []
    for device_id in range(1, number_of_devices + 1):
        t = threading.Thread(target=handle_uploader_concurrent,
                             args=[device_id, iterations, number_of_devices])
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


def run_datacli_serial(number_of_devices, iterations, frame_size, data_size):
    for iteration in range(1, iterations + 1):
        subprocess.call("adb shell logcat -c", shell=True)
        print(yellow(f"Starting iteration {iteration}"))
        for device_id in range(1, number_of_devices + 1):
            print(yellow(f"Starting Data_cli on device id={device_id}"))
            run_command(prefix.format(
                f"STRESS_DATA --ei id {device_id} --ei framesize {frame_size} --ei datasize {data_size} --ez turnaround true"))
            if device_id <= number_of_devices:
                command = "adb shell logcat"
                string_to_look_for = "AmaClientService: ==== Stress Data Test Finished ===="
                p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
                if not p.stdout:
                    print(red("Failed to pipe stdout of command: " + " ".join(command)))
                    sys.exit()
                while True:
                    line_bytes = p.stdout.readline()
                    line = line_bytes.decode('ISO-8859-15').strip()
                    if string_to_look_for in line:
                        sleep(1.5)
                        break
        else:
            print(red("Error iteration {}".format(iteration)))
            pass

    print(yellow(f"Data_cli to {number_of_devices} device(s) completed {iterations} iteration(s)"))
    return


def handle_datacli_concurrent(device_id, iterations, number_of_devices, frame_size, data_size):
    for iteration in range(1, iterations + 1):
        subprocess.call("adb shell logcat -c", shell=True)
        counter = 0
        print(yellow(f"Starting data_cli on device ID: {device_id} Iteration: {iteration}"))
        run_command(prefix.format(
            f"STRESS_DATA --ei id {device_id} --ei framesize {frame_size} --ei datasize {data_size} --ez turnaround true"))
        command = "adb shell logcat"
        string_to_look_for = "AmaClientService: ==== Stress Data Test Finished ===="
        p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
        if not p.stdout:
            print("failed to pipe stdout of command: " + " ".join(command))
            sys.exit()
        while True:
            line_bytes = p.stdout.readline()
            line = line_bytes.decode('ISO-8859-15').strip()
            if string_to_look_for in line:
                counter += 1
                if int(counter) >= number_of_devices:
                    sleep(2)
                    print(yellow(f"Data_cli completed on ID{device_id} for iteration {iteration}"))
                    break


def run_datacli_concurrent(number_of_devices, iterations, frame_size, data_size):
    threads = []
    for device_id in range(1, number_of_devices + 1):
        t = threading.Thread(target=handle_datacli_concurrent,
                             args=[device_id, iterations, number_of_devices, frame_size, data_size])
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


def run_ota(number_of_devices, iterations):
    check_ota_file = subprocess.check_output(f"adb shell ls /data/data/com.amazon.bt.amatest/files/dfu/",
                                             shell=True,
                                             encoding="utf-8").split('\n')
    if 'spartan.gbl' not in check_ota_file:
        print(yellow("spartan.gbl file is not pushed to EFD"))
        return
    else:
        for iteration in range(1, iterations + 1):
            subprocess.call("adb shell logcat -c", shell=True)
            print(yellow(f"Starting iteration {iteration}"))
            for device_id in range(1, number_of_devices + 1):
                print(yellow(f"starting OTA on device ID {device_id}"))
                run_command(prefix.format(f"START_TEST_DFU --ei id {device_id} --es file spartan.gbl"))
                if device_id <= number_of_devices:
                    if number_of_devices == 1:
                        command = "adb shell logcat"
                        string_to_look_for = f"Connection Complete - Device [{device_id}]"
                        p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
                        if not p.stdout:
                            print("failed to pipe stdout of command: " + " ".join(command))
                            sys.exit()
                        while True:
                            line_bytes = p.stdout.readline()
                            line = line_bytes.decode('ISO-8859-15').strip()
                            if string_to_look_for in line:
                                sleep(5)
                                break
                    else:
                        command = "adb shell logcat"
                        string_to_look_for = f"Disconnection Complete [{device_id}]"
                        p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
                        if not p.stdout:
                            print("failed to pipe stdout of command: " + " ".join(command))
                            sys.exit()
                        while True:
                            line_bytes = p.stdout.readline()
                            line = line_bytes.decode('ISO-8859-15').strip()
                            if string_to_look_for in line:
                                break
                else:
                    print(red(f"Error iteration {device_id}"))
        print(yellow(f"OTA to {number_of_devices} device(s) completed {iterations} iteration(s)"))
        return


def handle_reset_concurrent(port, iterations, timer):
    for iteration in range(1, iterations + 1):
        print(yellow(f"starting iteration: {iteration} on a {timer} second timer"))
        port.write_cmd("reset reboot")
        sleep(timer)
        port.write_cmd("agt gw_sm num_gws")
        port.write_cmd("agt gw_sm gw_state 1")
        sleep(3)


def run_reset_concurrent(number_of_devices, iterations, timer):
    threads = []
    ports = port_list(number_of_devices)
    for port in ports:
        t = threading.Thread(target=handle_reset_concurrent, args=[port, iterations, timer])
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


def run_reset_serial(iterations, number_of_devices):
    ports = port_list(number_of_devices)
    for iteration in range(1, iterations + 1):
        subprocess.call("adb shell logcat -c", shell=True)
        for port in ports:
            print(yellow(f"Iteration {iteration}  Port: {port}"))
            port.write_cmd("reset reboot")
            command = "adb shell logcat"
            string_to_look_for = "Connection Complete - Device"
            p = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, shell=True)
            if not p.stdout:
                print("failed to pipe stdout of command: " + " ".join(command))
                sys.exit()
            while True:
                line_bytes = p.stdout.readline()
                line = line_bytes.decode('ISO-8859-15').strip()
                if string_to_look_for in line:
                    sleep(5)
                    break
            port.write_cmd("agt gw_sm num_gws")
            port.write_cmd("agt gw_sm gw_state 1")
        sleep(120)


def run_command(command):
    """
    run_command: runs adb commands to the device in the order received.
    """
    send_command = subprocess.Popen([arg for arg in str(command).split()], stdin=subprocess.PIPE)
    while True:
        return_code = send_command.poll()
        if return_code is not None:
            return


def main():

    global iterations, number_of_devices, frame_size, data_size, timer
    options = ['Enable_Auto-register',
               'Connect_Accessory',
               'OTA',
               'Uploader_Serial',
               'Uploader_Concurrent',
               'DataCLI_Serial',
               'DataCLI_Concurrent',
               'Reset_Serial',
               'Reset_Concurrent']
    try:
        while True:
            for i in range(len(options)):
                print(str(i + 1) + ' - ' + options[i])
            answer = input('Please make a selection: ')
            if answer >= '2':
                number_of_devices = int(input("Enter number of devices: "))
            if answer >= '3':
                iterations = int(input("Enter number of iterations: "))
            if answer == '6':
                frame_size = int(input("Enter Frame_size:  "))
                data_size = int(input("Enter Data_size:  "))
            if answer == '7':
                frame_size = int(input("Enter Frame_size:  "))
                data_size = int(input("Enter Data_size:  "))
            if answer == '9':
                timer = int(input("Enter sleep time:  "))
            if answer == '1':
                print(yellow("Enabling Auto Register"))
                run_command(f"adb shell am broadcast -a com.amazon.amatest.ENABLE_AUTO_REGISTER")
                sleep(5)
                run_command("adb reboot")
            elif answer == '2':
                connect_accessory(number_of_devices)
            elif answer == '3':
                run_ota(number_of_devices, iterations)
            elif answer == '4':
                run_uploader_serial(number_of_devices, iterations)
            elif answer == '5':
                run_uploader_concurrent(number_of_devices, iterations)
            elif answer == '6':
                run_datacli_serial(number_of_devices, iterations, frame_size, data_size)
            elif answer == '7':
                run_datacli_concurrent(number_of_devices, iterations, frame_size, data_size)
            elif answer == '8':
                run_reset_serial(iterations, number_of_devices)
            elif answer == '9':
                run_reset_concurrent(number_of_devices, iterations, timer)



    except KeyboardInterrupt:
        print('Goodbye!')
        sys.exit()


if __name__ == "__main__":
    main()
