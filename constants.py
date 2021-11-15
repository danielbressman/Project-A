#!/usr/bin/env python3
# Written by Daniel Bressman

class Constants:

    def __init__(self):
        self.START_LE_SCAN = 'adb shell am broadcast -a com.amazon.amatest.START_LE_SCAN --ei scanduration 5 --ez block true'
        self.STOP_LE_SCAN = 'adb shell am broadcast -a com.amazon.amatest.STOP_LE_SCAN'
        self.ADD_ACCESSORY = 'adb shell am broadcast -a com.amazon.amatest.ADD_ACCESSORY --es address '
        self.PAIRED_LIST = 'adb shell am broadcast -a com.amazon.amatest.PAIRED_LIST'
        self.REMOVE_ACCESSORY = 'adb shell am broadcast -a com.amazon.amatest.REMOVE_ACCESSORY --es address '
        self.spartan_pair = 'agt oobe pair_new 0'
        self.bdaddress = '5B:86:25:99:F3:1A'
