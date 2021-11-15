#!/usr/bin/python3

#written by Daniel Bressman

import subprocess
import sys
from time import sleep

def cmd_res(cmd):
    p = subprocess.Popen([arg for arg in str(cmd).split()], stdin=subprocess.PIPE)
    p.wait()
    if p.returncode == 0:
        return 0
    else:
        return 1

def check_err(msg, ret):
    if ret != 0:
        print(f"ERROR: {msg}")
    else:
        print("success")

cmd = "adb shell am broadcast -a com.amazon.amatest.{}"
stat = cmd_res(cmd.format("ENABLE_AUTO_REGISTER"))
if stat != 0:
    stat = cmd_res(cmd.format("ENABLE_AUTO_REGISTER"))
    check_err("check adb connection", stat)
    sys.exit(1)
stat = cmd_res("adb reboot")
print("\nDevice is now ready for OTA / Uploader testing.\n")
print("\nFor OTA adb push spartan.gbl /data/data/com.amazon.bt.amatest/files/dfu/\n")

