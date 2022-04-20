#!/usr/bin/python3

# written by Daniel Bressman

import os
import sys
import subprocess
from typing import Optional

yellow = lambda s: f"\033[93m{s}\033[00m"
red = lambda s: f"\033[91m{s}\033[00m"


class Device:

    wifi_location = 'wpa_cli status'

    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.device_name = self.get_device()
        self.os_version = self.get_os_version()
        self.build = self.get_build()
        self.bt_mac = self.get_bt_mac()
        self.wifi_mac = self.get_wifi_mac()
        self.wifi_ssid = self.get_wifi_ssid()
        self.wifi_security = self.get_wifi_security()
        self.wifi_band = self.get_wifi_band()
        self.wifi_channel = self.get_wifi_channel()
        self.paired_devices = self.get_paired_devices()

    def get_device(self) -> Optional[str]:
        """
        get_device: checks for the device name and filters the output.
        :return: returns the devices name.
        """
        output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop ro.product.name", shell=True,
                                         encoding="utf-8")
        product_name = output.split("\n")[0]
        if '_mt8512' in product_name:
            device_name = product_name.split("_mt8512")[0]
            return device_name.title()
        elif '_mt8512' not in product_name:
            device_name = product_name.split("_")[-1]
            return device_name.title()
        else:
            print(red("Could not the get devices name"))
        return

    def get_os_version(self) -> Optional[str]:
        """
        get_os_version: checks for the devices OS version and filters the output to determine if OS is ACE or FOS.
        :return: returns the devices OS version in either "ACE" or "FOS(int)" format.
        """
        output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop", shell=True,
                                         encoding="utf-8")
        if self.device_name == 'Lidar':
            return 'FOS6/ACE'
        elif 'puffin' in output:
            return "ACE"
        elif 'puffin' not in output:
            output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop ro.build.version.fireos",
                                             shell=True).decode()
            os_version = "FOS" + str(int(output[0].split(".")[0]))
            if os_version == 'FOS5':
                self.wifi_location = 'dumpsys wifi'
            return os_version
        else:
            print(red("Could not get devices OS version"))
        return

    def get_build(self) -> Optional[str]:
        """
        get_build: checks for the device build and filters the output.
        :return: returns the devices build.
        """
        output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop ro.build.fingerprint", shell=True,
                                         encoding="utf-8")
        device_build = output.split('\n')[0]
        if self.device_name.lower() in device_build:
            return device_build
        else:
            print(red('Could not get the devices build'))
        return

    def get_bt_mac(self) -> Optional[str]:
        """
        get_bt_mac: checks for the device BT mac address and filters the output.
        :return: returns the devices BT mac address.
        """
        directory_contents = subprocess.check_output(
            f"adb -s {self.serial_number} shell ls data/misc/bluedroid/", shell=True, encoding="utf-8").split('\n')
        target_extensions = ["conf", "xml", "bak"]
        file_extension = None
        for directory_file in directory_contents:
            if 'bt_config' in directory_file:
                file_extension = directory_file.split('.')[-1]
                if file_extension in target_extensions:
                    break
                else:
                    continue

        if not file_extension:
            print(red('Could not get the devices BT mac address'))
            return

        bt_mac = None
        output = subprocess.check_output(
            f"adb -s {self.serial_number} shell cat data/misc/bluedroid/bt_config.{file_extension} | grep Address",
            shell=True, encoding="utf-8")
        if file_extension == 'conf':
            bt_mac = output.split("=")[1][:18]
        elif file_extension == 'bak':
            bt_mac = output.split("=")[1][:18]
        elif file_extension == 'xml':
            output = subprocess.check_output(f"adb -s {self.serial_number} shell settings get secure bluetooth_address",
                                             shell=True, encoding="utf-8")
            if 'Address' in output:
                bt_mac = output.split('Address =')[:17]
            else:
                bt_mac = output[:17]
        else:
            print(red('Could not get the devices BT mac address'))
        return bt_mac.upper().strip()

    def get_wifi_mac(self) -> Optional[str]:
        """
        get_wifi_mac: checks for the device Wi-Fi mac address and filters the output.
        :return: returns the devices Wi-Fi mac address.
        """
        check_connection = subprocess.check_output(f"adb -s {self.serial_number} shell ifconfig", shell=True,
                                                   encoding="utf-8")
        if 'wlan' not in check_connection:
            wifi_state = 'Disconnected'
            return wifi_state
        output = subprocess.check_output(f"adb -s {self.serial_number} shell wpa_cli stat | grep -w address",
                                         shell=True, encoding="utf-8")
        if 'address' in output:
            address = output.split("=")[1].split("address")[0]
            wifi_mac = address.split('\n')[0]
            return wifi_mac.upper()

    def get_wifi_ssid(self) -> str:
        """
        get_wifi_ssid: checks for the devices connected Wi-Fi ssid and filters the output.
        :return: returns the devices connected Wi-Fi ssid.
        """
        if self.wifi_mac is 'Disconnected':
            return 'Disconnected'
        check_state = subprocess.check_output(f"adb -s {self.serial_number} shell {self.wifi_location}",
                                              shell=True, encoding="utf-8")
        if 'wpa_state=COMPLETED' in check_state:
            output = subprocess.check_output(f"adb -s {self.serial_number} shell {self.wifi_location}",
                                             shell=True, encoding="utf-8")
            if 'ssid' in output:
                ssid = output.split("=")[3].split("id")[0].strip()
                return ssid
        else:
            return 'Disconnected'

    def get_wifi_security(self) -> str:
        """
        get_wifi_security: checks for the devices connected Wi-Fi security type and filters the output.
        :return: returns the devices connected Wi-Fi security type.
        """
        if self.wifi_ssid is 'Disconnected':
            return 'Disconnected'
        output = subprocess.check_output(f"adb -s {self.serial_number} shell {self.wifi_location} | grep key_mgmt",
                                         shell=True, encoding="utf-8")
        if 'key_mgmt' in output:
            security_type = output.split("key_mgmt=")[1].strip()
            if security_type == 'NONE':
                security_type = 'Open'
            return security_type

    def get_wifi_band(self) -> str:
        """
        get_wifi_band: checks for the devices connected Wi-Fi band and filters the output.
        :return: returns the devices connected Wi-Fi band.
        """
        band = '2.4Ghz'
        if self.wifi_ssid is 'Disconnected':
            return 'Disconnected'
        output = subprocess.check_output(f"adb -s {self.serial_number} shell {self.wifi_location}",
                                         shell=True, encoding="utf-8")
        if 'freq' in output:
            freq = output.split("freq=")[1].strip()
            if freq >= '3000':
                band = '5Ghz'
            return band

    def get_wifi_channel(self) -> str:
        """
        get_wifi_channel: checks for the devices connected Wi-Fi channel and filters the output.
        :return: returns the devices connected Wi-Fi channel.
        """
        channel = None
        if self.wifi_ssid is 'Disconnected':
            return 'Disconnected'
        channels = {'2412': 1, '2417': 2, '2422': 3, '2427': 4, '2432': 5, '2437': 6, '2442': 7, '2447': 8, '2452': 9,
                    '2457': 10, '2462': 11, '2467': 12, '2472': 13, '2484': 14, '5160': 32, '5170': 34, '5180': 36,
                    '5190': 38, '5200': 40, '5210': 42, '5220': 44, '5230': 46, '5240': 48, '5250': 50, '5260': 52,
                    '5270': 54, '5280': 56, '5290': 58, '5300': 60, '5310': 62, '5320': 64, '5340': 68, '5480': 96,
                    '5500': 100, '5510': 102, '5520': 104, '5530': 106, '5540': 108, '5550': 110, '5560': 112,
                    '5570': 114, '5580': 116, '5590': 118, '5600': 120, '5610': 122, '5620': 124, '5630': 126,
                    '5640': 128, '5660': 132, '5670': 134, '5680': 136, '5690': 138, '5700': 140, '5710': 142,
                    '5720': 144, '5745': 149, '5755': 151, '5765': 153, '5775': 155, '5785': 157, '5795': 159,
                    '5805': 161, '5815': 163, '5825': 165, '5835': 167, '5845': 169, '5855': 171, '5865': 173,
                    '5875': 175, '5885': 177, '5910': 182, '5915': 183, '5920': 184, '5935': 187, '5940': 188,
                    '5945': 189, '5960': 192, '5980': 196}
        output = subprocess.check_output(f"adb -s {self.serial_number} shell {self.wifi_location} | grep 'freq'",
                                         shell=True, encoding="utf-8")
        if 'freq' in output:
            freq = output.split("=")[1].strip()
            for frequency, value in channels.items():
                if freq in frequency:
                    channel = value
            return channel

    def get_paired_devices(self) -> dict:
        """
        get_pared_devices: checks for the devices paired via Bluetooth and filters the output.
        :return: returns the name and BT mac address of all paired devices.
        """
        paired_devices = {}
        directory_contents = subprocess.check_output(f"adb -s {self.serial_number} shell ls data/misc/bluedroid/",
                                                     shell=True, encoding="utf-8").split('\n')
        target_extensions = ["conf", "xml", "bak"]
        file_extension = None
        for directory_file in directory_contents:
            if 'bt_config' in directory_file:
                file_extension = directory_file.split('.')[-1]
                if file_extension in target_extensions:
                    break
                else:
                    continue

        if not file_extension:
            print(red('Could not get the devices paired list'))
            return paired_devices

        paired_address = subprocess.check_output(
            f"adb -s {self.serial_number} shell cat data/misc/bluedroid/bt_config.{file_extension} | grep -P 'Name =|\[.*?\]' | tail -n +4",
            shell=True, encoding="utf-8")
        paired_address_list = paired_address.rstrip("\n").split('[')
        for line in paired_address_list:
            if 'Name =' in line:
                name = line.rstrip("\n").split("Name = ")[1]
                address = line[:17]
                paired_devices[str(name)] = str(address).upper()
        return paired_devices

    def handle_directories(self) -> None:
        """
        handle_directories: generates directories to store log files.
        """
        root_folder = os.getcwd()
        if os.getcwd != root_folder:
            os.chdir(root_folder)
        print(yellow(f"Pulling logs from {self.device_name} {self.serial_number}"))
        if not os.getcwd() == root_folder:
            os.chdir(root_folder)
        device_folder = os.path.join(root_folder, f"{self.device_name}")
        if not os.path.exists(device_folder):
            os.mkdir(device_folder)
        os.chdir(f"{self.device_name}")
        serial_folder = os.path.join(f"{self.serial_number}_logs_")
        counter = 1
        while True:
            if os.path.exists(serial_folder + str(counter)):
                counter += 1
            else:
                serial_folder = serial_folder + str(counter)
                break
        if not os.path.exists(serial_folder):
            os.mkdir(serial_folder)
        os.chdir(serial_folder)

    def get_bt_logs(self) -> None:
        """
        get_bt_logs: pulls various types of logs from the device.
        """
        run_command(f"adb -s {self.serial_number} pull /data/misc/bluedroid")
        run_command(f"adb -s {self.serial_number} pull /data/misc/bluetooth")
        run_command(f"adb -s {self.serial_number} pull /data/misc/blemesh")
        run_command(f"adb -s {self.serial_number} pull /data/misc/smarthome_shared")
        run_command(f"adb -s {self.serial_number} pull /data/tombstones")
        run_command(f"adb -s {self.serial_number} pull /data/misc/ama/ama.bin")
        if self.os_version == "FOS5":
            run_command(f"adb -s {self.serial_number} pull /sdcard/btsnoop_hci.log btsnoophci")

    def print_text_file(self) -> None:
        """
        print_text_file: generates the Device_info file which contains crucial device information.
        """
        with open("Device_info.txt", "w") as text_file:
            print(f"Device: {self.device_name}", file=text_file)
            print(f"DSN: {self.serial_number}", file=text_file)
            print(f"Build: {self.build}", file=text_file)
            print(f"OS version: {self.os_version}", file=text_file)
            print(f"BT MAC: {self.bt_mac}", file=text_file)
            print(f"Wifi MAC: {self.wifi_mac}", file=text_file)
            print(f"Wifi SSID: {self.wifi_ssid}", file=text_file)
            print(f"Wifi security: {self.wifi_security}", file=text_file)
            print(f"Wifi band: {self.wifi_band}", file=text_file)
            print(f"Wifi channel: {self.wifi_channel}", file=text_file)
            if len(self.paired_devices) >= 1:
                print("\nPaired Devices:", file=text_file)
                for name, address in self.paired_devices.items():
                    print(name, address, file=text_file)

    def print_device_info(self) -> None:
        """
        print_device_info: prints the device information to the terminal.
        """
        print(f"Device: {self.device_name}")
        print(f"DSN: {self.serial_number}")
        print(f"Build: {self.build}")
        print(f"OS version: {self.os_version}")
        print(f"BT MAC: {self.bt_mac}")
        print(f"Wifi MAC: {self.wifi_mac}")
        print(f"Wifi SSID: {self.wifi_ssid}")
        print(f"Wifi security: {self.wifi_security}")
        print(f"Wifi band: {self.wifi_band}")
        print(f"Wifi channel: {self.wifi_channel}")
        if len(self.paired_devices) >= 1:
            print("Paired Devices:")
            for name, address in self.paired_devices.items():
                print(name, address)


def get_adb_devices() -> list:
    """
    get_adb_devices: checks for available adb devices and filters them to a list.
    :return: returns list of adb devices
    """
    output = subprocess.check_output(["adb", "devices"]).decode("ISO-8859-15")
    output = output.splitlines()
    devices = []
    for line in output[1:]:
        if "device" in line:
            devices.append(line[:-7])
    return devices


def run_command(command) -> None:
    """
    run_command: runs adb commands to the device in the order received.
    """
    send_command = subprocess.Popen([arg for arg in str(command).split()])
    while True:
        return_code = send_command.poll()
        if return_code is not None:
            break
    return


usage = \
    f"""
Usage: python3 {__file__} <optional_parameter>

    Automation for pulling and sorting logs from android device(s).
    Folder structure: device_name -> device_serial_# -> logs.
    Device_serial folder starts at 1 and iterates up to prevent overwritten files.
    Device_serial folder contains text file "Device_info.txt" which shows crucial device info.
    Can be used with any number of ADB devices at a time, files will match each device.

    python3 {__file__}                         Runs the logging automation.
    python3 {__file__} -h                      Prints this help message.
    python3 {__file__} -(anything else)        Prints the device information to terminal.    
"""


def main() -> None:
    devices = get_adb_devices()
    device_objs = []
    for serial_number in devices:
        device_objs.append(Device(serial_number))
    for dsn in device_objs:
        root_folder = os.getcwd()
        if os.getcwd != root_folder:
            os.chdir(root_folder)
        if len(sys.argv) >= 2:
            if str(sys.argv[1]) == "-h":
                print(yellow(usage))
                sys.exit(1)
            else:
                dsn.print_device_info()
                pass
        else:
            dsn.handle_directories()
            dsn.get_bt_logs()
            dsn.print_text_file()
            serial_folder = os.getcwd()
            print(yellow(f"Logs pulled to {serial_folder}"))
        os.chdir(root_folder)


if __name__ == "__main__":
    main()
