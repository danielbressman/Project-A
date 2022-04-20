#!/usr/bin/python3

# written by Daniel Bressman

import os
import sys
from time import sleep
import subprocess
from typing import Optional

red = lambda s: "\033[91m{}\033[00m".format(s)
yellow = lambda s: "\033[93m{}\033[00m".format(s)


FOS5 = """# Enable BtSnoop logging function
# valid value : true, false
BtSnoopLogOutput=true

# BtSnoop log output file
BtSnoopFileName=/sdcard/btsnoop_hci.log

# Preserve existing BtSnoop log before overwriting
BtSnoopSaveLog=true

# Enable trace level reconfiguration function
# Must be present before any TRC_ trace level settings
TraceConf=true

# Trace level configuration
#   BT_TRACE_LEVEL_NONE    0    ( No trace messages to be generated )
#   BT_TRACE_LEVEL_ERROR   1    ( Error condition trace messages )
#   BT_TRACE_LEVEL_WARNING 2    ( Warning condition trace messages )
#   BT_TRACE_LEVEL_API     3    ( API traces )
#   BT_TRACE_LEVEL_EVENT   4    ( Debug messages for events )
#   BT_TRACE_LEVEL_DEBUG   5    ( Full debug messages )
#   BT_TRACE_LEVEL_VERBOSE 6    ( Verbose messages ) - Currently supported for TRC_BTAPP only.
TRC_BTM=6
TRC_HCI=6
TRC_L2CAP=6
TRC_RFCOMM=6
TRC_OBEX=6
TRC_AVCT=6
TRC_AVDT=6
TRC_AVRC=6
TRC_AVDT_SCB=6
TRC_AVDT_CCB=6
TRC_A2D=6
TRC_SDP=6
TRC_GATT=6
TRC_SMP=6
TRC_BTAPP=6
TRC_BTIF=6
"""

FOS6 = """# Enable BtSnoop logging function
# valid value : true, false
BtSnoopLogOutput=true

# BtSnoop log output file
BtSnoopFileName=/data/misc/bluetooth/logs/btsnoop_hci.log

# Preserve existing BtSnoop log before overwriting
BtSnoopSaveLog=true

# Enable trace level reconfiguration function
# Must be present before any TRC_ trace level settings
TraceConf=true

# Trace level configuration
#   BT_TRACE_LEVEL_NONE    0    ( No trace messages to be generated )
#   BT_TRACE_LEVEL_ERROR   1    ( Error condition trace messages )
#   BT_TRACE_LEVEL_WARNING 2    ( Warning condition trace messages )
#   BT_TRACE_LEVEL_API     3    ( API traces )
#   BT_TRACE_LEVEL_EVENT   4    ( Debug messages for events )
#   BT_TRACE_LEVEL_DEBUG   5    ( Full debug messages )
#   BT_TRACE_LEVEL_VERBOSE 6    ( Verbose messages ) - Currently supported for TRC_BTAPP only.
TRC_BTM=6
TRC_HCI=6
TRC_L2CAP=6
TRC_RFCOMM=6
TRC_OBEX=6
TRC_AVCT=6
TRC_AVDT=6
TRC_AVRC=6
TRC_AVDT_SCB=6
TRC_AVDT_CCB=6
TRC_A2D=6
TRC_SDP=6
TRC_GATT=6
TRC_SMP=6
TRC_BTAPP=6
TRC_BTIF=6
TRC_GAP=6
TRC_BNEP=6
TRC_PAN=6

# PTS testing helpers

# Secure connections only mode.
# PTS_SecurePairOnly=true

# Disable LE Connection updates
#PTS_DisableConnUpdates=true

# Disable BR/EDR discovery after LE pairing to avoid cross key derivation errors
#PTS_DisableSDPOnLEPair=true

# SMP Pair options (formatted as hex bytes) auth, io, ikey, rkey, ksize
#PTS_SmpOptions=0xD,0x4,0xf,0xf,0x10

# SMP Certification Failure Cases
# Fail case number range from 1 to 9 will set up remote device for test
# case execution. Setting PTS_SmpFailureCase to 0 means normal operation.
# Failure modes:
#  1 = SMP_CONFIRM_VALUE_ERR
#  2 = SMP_PAIR_AUTH_FAIL
#  3 = SMP_PAIR_FAIL_UNKNOWN
#  4 = SMP_PAIR_NOT_SUPPORT
#  5 = SMP_PASSKEY_ENTRY_FAIL
#  6 = SMP_REPEATED_ATTEMPTS
#  7 = PIN generation failure?
#  8 = SMP_PASSKEY_ENTRY_FAIL
#  9 = SMP_NUMERIC_COMPAR_FAIL;
#PTS_SmpFailureCase=0
"""

FOS7 = """# Enable trace level reconfiguration function
# Must be present before any TRC_ trace level settings
TraceConf=true

# Trace level configuration
#   BT_TRACE_LEVEL_NONE    0    ( No trace messages to be generated )
#   BT_TRACE_LEVEL_ERROR   1    ( Error condition trace messages )
#   BT_TRACE_LEVEL_WARNING 2    ( Warning condition trace messages )
#   BT_TRACE_LEVEL_API     3    ( API traces )
#   BT_TRACE_LEVEL_EVENT   4    ( Debug messages for events )
#   BT_TRACE_LEVEL_DEBUG   5    ( Full debug messages )
#   BT_TRACE_LEVEL_VERBOSE 6    ( Verbose messages ) - Currently supported for TRC_BTAPP only.
TRC_BTM=6
TRC_HCI=6
TRC_L2CAP=6
TRC_RFCOMM=6
TRC_OBEX=6
TRC_AVCT=6
TRC_AVDT=6
TRC_AVRC=6
TRC_AVDT_SCB=6
TRC_AVDT_CCB=6
TRC_A2D=6
TRC_SDP=6
TRC_SMP=6
TRC_BTAPP=6
TRC_BTIF=6
TRC_BNEP=6
TRC_PAN=6
TRC_HID_HOST=6
TRC_HID_DEV=6

# This is Log configuration for new C++ code using LOG() macros.
# See libchrome/base/logging.h for description on how to configure your logs.
# sample configuration:
LoggingV=--v=0
LoggingVModule=--vmodule=*/btm/*=1,btm_ble_multi*=2,btif_*=1

# PTS testing helpers

# Secure connections only mode.
# PTS_SecurePairOnly=true

# Disable LE Connection updates
#PTS_DisableConnUpdates=true

# Disable BR/EDR discovery after LE pairing to avoid cross key derivation errors
#PTS_DisableSDPOnLEPair=true

# SMP Pair options (formatted as hex bytes) auth, io, ikey, rkey, ksize
#PTS_SmpOptions=0xD,0x4,0xf,0xf,0x10

# PTS AVRCP Test mode
#PTS_AvrcpTest=true

# SMP Certification Failure Cases
# Set any of the following SMP error values (from smp_api_types.h)
# to induce pairing failues for various PTS SMP test cases.
# Setting PTS_SmpFailureCase to 0 means normal operation.
# Failure modes:
#
#  SMP_PASSKEY_ENTRY_FAIL = 1
#  SMP_PAIR_AUTH_FAIL = 3
#  SMP_CONFIRM_VALUE_ERR = 4
#  SMP_PAIR_NOT_SUPPORT = 5
#  SMP_PAIR_FAIL_UNKNOWN = 8
#  SMP_REPEATED_ATTEMPTS = 9
#  SMP_NUMERIC_COMPAR_FAIL = 12
#PTS_SmpFailureCase=0
"""

ACE = """# Enable BtSnoop logging function
# valid value : true, false
BtSnoopLogOutput=true

# BtSnoop log output file
BtSnoopFileName=/data/misc/bluetooth/logs/btsnoop_hci.log

# Preserve existing BtSnoop log before overwriting
BtSnoopSaveLog=true

# Enable trace level reconfiguration function
# Must be present before any TRC_ trace level settings
TraceConf=true

# Trace level configuration
#   BT_TRACE_LEVEL_NONE    0    ( No trace messages to be generated )
#   BT_TRACE_LEVEL_ERROR   1    ( Error condition trace messages )
#   BT_TRACE_LEVEL_WARNING 2    ( Warning condition trace messages )
#   BT_TRACE_LEVEL_API     3    ( API traces )
#   BT_TRACE_LEVEL_EVENT   4    ( Debug messages for events )
#   BT_TRACE_LEVEL_DEBUG   5    ( Full debug messages )
#   BT_TRACE_LEVEL_VERBOSE 6    ( Verbose messages ) - Currently supported for TRC_BTAPP only.
TRC_BTM=6
TRC_HCI=6
TRC_L2CAP=6
TRC_RFCOMM=6
TRC_OBEX=6
TRC_AVCT=6
TRC_AVDT=6
TRC_AVRC=6
TRC_AVDT_SCB=6
TRC_AVDT_CCB=6
TRC_A2D=6
TRC_SDP=6
TRC_GATT=6
TRC_SMP=6
TRC_BTAPP=6
TRC_BTIF=6
TRC_GAP=6
TRC_BNEP=6
TRC_PAN=6

# PTS testing helpers

# Secure connections only mode.
# PTS_SecurePairOnly=true

# Disable LE Connection updates
#PTS_DisableConnUpdates=true

# Disable BR/EDR discovery after LE pairing to avoid cross key derivation errors
#PTS_DisableSDPOnLEPair=true

# SMP Pair options (formatted as hex bytes) auth, io, ikey, rkey, ksize
#PTS_SmpOptions=0xD,0x4,0xf,0xf,0x10

# SMP Certification Failure Cases
# Fail case number range from 1 to 9 will set up remote device for test
# case execution. Setting PTS_SmpFailureCase to 0 means normal operation.
# Failure modes:
#  1 = SMP_CONFIRM_VALUE_ERR
#  2 = SMP_PAIR_AUTH_FAIL
#  3 = SMP_PAIR_FAIL_UNKNOWN
#  4 = SMP_PAIR_NOT_SUPPORT
#  5 = SMP_PASSKEY_ENTRY_FAIL
#  6 = SMP_REPEATED_ATTEMPTS
#  7 = PIN generation failure?
#  8 = SMP_PASSKEY_ENTRY_FAIL
#  9 = SMP_NUMERIC_COMPAR_FAIL;
#PTS_SmpFailureCase=0
"""


class Device:
    def __init__(self, serial_number):
        self.serial_number = serial_number
        self.device_name = self.get_device()
        self.os_version = self.get_os_version()

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
            return device_name
        elif '_mt8512' not in product_name:
            device_name = product_name.split("_")[-1]
            return device_name.title()
        else:
            print(red("Could not the get the devices name"))
        return

    def get_os_version(self) -> Optional[str]:
        """
        get_os_version: checks for the devices OS version and filters the output to determine if OS is ACE or FOS.
        :return: returns the devices OS version in either "ACE" or "FOS(int)" format.
        """
        output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop", shell=True,
                                         encoding="utf-8")
        if 'puffin' in output:
            return "ACE"
        elif 'puffin' not in output:
            output = subprocess.check_output(f"adb -s {self.serial_number} shell getprop ro.build.version.fireos",
                                             shell=True).decode()
            version = int(output[0].split(".")[0])
            return "FOS" + str(version)
        else:
            print(red("Could not get the devices OS version"))
        return

    def enable_stack6(self) -> None:
        """
        enable_stack6: enables stack6 logging to be used with bt_logs.
        """
        if len(sys.argv) >= 2:
            print(yellow(f"Enabling stack6 logging on {self.device_name} {self.serial_number}"))
        run_command(f"adb -s {self.serial_number} shell setprop log.tag.ControllerManagerLogs DEBUG")
        run_command(f"adb -s {self.serial_number} shell setprop persist.bt.logging true")
        run_command(f"adb -s {self.serial_number} shell setprop persist.bluetooth.stack_logging 6")
        run_command(f"adb -s {self.serial_number} shell setprop persist.bluetooth.btsnoop_time 1")
        run_command(f"adb -s {self.serial_number} shell setprop persist.bluetooth.btsnoopenable true")
        sleep(2)
        if len(sys.argv) >= 2:
            print(yellow(f"Success, rebooting {self.device_name} {self.serial_number} now..."))
            run_command(f"adb -s {self.serial_number} reboot")

    def enable_bt_logs(self) -> None:
        """
        enable_bt_logs: enables bt snoop logs required for most JIRAs.
        """
        version = None
        if self.os_version == 'FOS5':
            version = FOS5
        elif self.os_version == 'FOS6':
            version = FOS6
        elif self.os_version == 'FOS7':
            version = FOS7
        elif self.os_version == 'ACE':
            version = ACE
        elif version is None:
            print(red("Could not get device OS version"))
            return
        print(yellow(f"Enabling bt logs on {self.device_name} {self.serial_number}"))
        run_command(f"adb -s {self.serial_number} pull /etc/bluetooth/bt_stack.conf")
        with open("bt_stack.conf", "w") as text_file:
            text_file.write(version)
            text_file.close()
        run_command(f"adb -s {self.serial_number} push bt_stack.conf /etc/bluetooth/")
        sleep(0.5)
        print(yellow(f"Success, rebooting {self.device_name} {self.serial_number} now..."))
        run_command(f"adb -s {self.serial_number} reboot")
        return


def run_command(command) -> None:
    """
    run_command: runs adb commands to the device in the order received.
    """
    send_command = subprocess.Popen([arg for arg in str(command).split()])
    send_command.wait()
    while True:
        return_code = send_command.poll()
        if return_code is not None:
            break
    return


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


usage = \
    f"""
Usage: python3 {__file__} <optional_parameter>

    Automation for enabling stack6 and bt snoop logs for Android device(s).
    Detects which OS version is being used and enables correct logging based on that.
    Can be used with any number of ADB devices at the same time.

    python3 {__file__}                         Runs the logging automation.
    python3 {__file__} -h                      Prints this help message.
    python3 {__file__} -(anything else)        Only enables stack6 logging.    
"""


def main():
    root_folder = os.getcwd()
    devices = get_adb_devices()
    device_objs = []
    for serial_number in devices:
        device_objs.append(Device(serial_number))
    for dsn in device_objs:
        subprocess.check_output(f"adb -s {dsn.serial_number} root", shell=True)
        subprocess.check_output(f"adb -s {dsn.serial_number} remount", shell=True)
        if len(sys.argv) >= 2:
            if str(sys.argv[1]) == "-h":
                print(yellow(usage))
                sys.exit(1)
            else:
                dsn.enable_stack6()
        else:
            dsn.enable_stack6()
            dsn.enable_bt_logs()
            if os.path.exists(os.path.join(root_folder, "bt_stack.conf")):
                os.remove(os.path.join(root_folder, "bt_stack.conf"))


if __name__ == "__main__":
    main()
