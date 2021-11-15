#!/usr/bin/env python3
# Written by Daniel Bressman


import datetime
import logging as log
from constants import Constants
import re
from terminal_commands import store_output
from serial_controller import run_command
import argparse
import sys

class Ble:

    def __init__(self):
        self.address_found = False
        self.bd_address = None
        self.add_accessory = False
        self.pass_status = False
        self.remove = False
        self.paired = False
        self.constants = Constants()

    def start_le_scan(self, blocking=True):
        self.spartan_pair()
        log.info("Sending LE scan command")
        cmd = self.constants.spartan_pair
        if blocking:
            res, output = self.send_adb_command(self.constants.START_LE_SCAN)
            output = str(output)
            log.info(output)
            if res and len(output) > 0:
                # scan_result = re.findall('\[.*?\]',str(output))
                scan_result = output.split('[')
                print(scan_result)
                for i in scan_result:
                    if 'name=GadgetDemo' in i:
                        log.info("entered loop")
                        # pat = re.compile('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}')
                        # found = re.search(pat, i)

                        found = i.split('address=')[1][:17]
                        log.info("the above address is found")
                        log.info(found)
                        print('the above address is found')
                        print(found)
                        if found:
                            self.address_found = True
                            log.info("'START_LE_SCAN' command sent successfully "
                                     "and Spartan address found is: {}".format(found))
                            self.bd_address = found
                            log.info(self.bd_address)
                            # self.send_adb_command(self.constants.STOP_LE_SCAN)
                            return self.bd_address
                        else:
                            log.info("No BD address found")
                            self.address_found = False
                log.error('No Spartan beacons found during the scan')
            else:
                log.error(" The start scan command was not sent successfully")

    def add_spartan(self):
        log.info("Pairing Spartan to Echo device")
        if self.bd_address:
            command = self.constants.ADD_ACCESSORY + self.bd_address
            res, output = self.send_adb_command(command, time_out=15)
            log.info(output)
            if res and len(output) > 0:
                for i in output:
                    if "PAIR:Sent command successfully" in i:
                        self.add_accessory = True
                        log.info("Able to send add accessory command, stopped LE scan and paired Spartan")
            else:
                log.error("Unable to verify add accessory command need to check from LIST ACCESSORY")
                self.pass_status = False
            if not self.add_accessory:
                log.error("Unable to add Spartan to Cronos")
                self.pass_status = False

    def spartan_pair(self, check_timeout=False, timeout=5):
        cmd = self.constants.spartan_pair
        try:
            log.info("Putting Spartan in pairing mode")
            log.info(cmd)
            if check_timeout:
                timeout = 35
            output = run_command(cmd, '/dev/ttyACM0', 115200)
            output = str(output)
            print(output)
            if any('AGT:AppSm:Adv for pairing' in x for x in output) and \
                    any('AGT:AppSm:Test_Magic:AmaAdv,ret=0,msg={Enter pairing mode}' in x for x in output):
                log.info("Spartan is set in pairing mode verified")
                self.pass_status = True
                if check_timeout:
                    pat = re.compile(r"\w{4}-\w{2}-\w{2}\s\w{2}:\w{2}:\w{2}\.\w{3}")
                    start_time = datetime.date
                    end_time = datetime.date
                    for line in output:
                        if 'AGT:AppSm:Started Ama adv' in line:
                            start_search = re.search(pat, line)
                            start_time = datetime.strptime(start_search.group(), "%Y-%m-%d %H:%M:%S.%f")
                        if "AGT:AppSm:Pairing timeout" in line:
                            end_search = re.search(pat, line)
                            end_time = datetime.strptime(end_search.group(), "%Y-%m-%d %H:%M:%S.%f")
                    time_diff = (end_time - start_time).seconds
                    if time_diff == 30:
                        log.info("Pairing timeout is 30s and is expected")
                        self.pass_status = True
                    else:
                        log.error("Pairing timeout is not 30s")
                        self.pass_status = False
            else:
                log.error("Spartan did not go to pairing mode")
                self.pass_status = False

        except Exception as e:
            log.error("Unable to set Spartan to pairing mode due to {}".format(e))
            self.pass_status = False

    def paired_list(self):
        log.info("Checking devices paired to Echo device")
        command = self.constants.PAIRED_LIST
        res, output = self.send_adb_command(command, time_out=5)
        log.info(output)
        if res and len(output) > 0:
            for i in output:
                if "GadgetDemo" in i:
                    pat = re.compile('\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}')
                    found = re.search(pat, i)
                    if found.group() == self.bd_address:
                        self.paired = True
                        self.pass_status = True
            if self.paired:
                log.info("Spartan {} is paired to EFD".format(self.bd_address))
            else:
                log.info("No Spartan is paired to EFD")
                return
        else:
            log.error("Unable to verify paired list command")
            self.pass_status = False
        if not self.add_accessory:
            log.error("Unable to add Spartan to Cronos")
            self.pass_status = False

    def remove_spartan(self):
        log.info("Removing Spartan paired to EFD")
        if self.bd_address:
            command = self.constants.REMOVE_ACCESSORY + self.bd_address
            res, output = self.send_adb_command(command, time_out=5)
            if res and len(output) > 0:
                for i in output:
                    if "Command[REMOVE_BOND] sent successfully" in i:
                        self.remove = True
                        self.pass_status = True
                if self.remove:
                    log.info("Remove Spartan from EFD sent successfully")
                else:
                    log.info("Unable to remove Spartan from EFD")
            else:
                log.error("Unable to send remove command")

    @staticmethod
    def send_adb_command(command, time_out=None):
        output = store_output(command, timeout=time_out)
        if not output:
            return (False, False)
        else:
            return (True, output)


def main():
    ble_test = Ble()
    parser = argparse.ArgumentParser()
    log.basicConfig(level=log.INFO)
    parser.add_argument('-s', '--scan', action='store_true', help='starts le scan')
    parser.add_argument('-p', '--pair', action='store_true', help='pair le device')
    parser.add_argument('-u', '--unpair', action='store_true', help='unpair le device')

    args = parser.parse_args()

    if args.scan:
        # Start scan
        ble_test.start_le_scan()

    elif args.pair:
        # Put spartan in pairing mode
        # ble_test.spartan_pair()
        # Start scan
        ble_test.start_le_scan()
        # Pair with spartan
        ble_test.add_spartan()
        # Verify paired list
        ble_test.paired_list()

    elif args.unpair:
        # Remove Spartan
        ble_test.remove_spartan()

    else:
        options = ['Scan',
                   'Pair',
                   'Unpair']
        try:
            while True:
                for i in range(len(options)):
                    print(str(i+1) + ' - '+options[i])
                answer = input('Please make a selection: ')
                if answer == '1':
                    ble_test.start_le_scan()
                elif answer == '2':
                    # Start scan
                    ble_test.start_le_scan()
                    # Pair with spartan
                    ble_test.add_spartan()
                    # Verify paired list
                    ble_test.paired_list()
                elif answer == '3':
                    # Remove Spartan
                    ble_test.remove_spartan()
                else:
                    print('Invalid selection')

        except KeyboardInterrupt:
            print('Goodbye!')
            sys.exit()


if __name__ == '__main__':
    main()

