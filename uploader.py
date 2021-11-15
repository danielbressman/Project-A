#!/usr/bin/python3

#written by Daniel Bressman

import subprocess
import sys
import re
from time import sleep

USAGE = """Usage: uploader.py <num_devices> [iterations]"""
iterations = 1
if len(sys.argv) < 2:
    print(USAGE)

if len(sys.argv) >= 3:
    iterations = int(sys.argv[2])

num_devs = int(sys.argv[1])
prefix = "adb shell am broadcast -a com.amazon.amatest.{}"
res = re.compile(r"^Broadcasting: Intent { act=com.amazon.amatest.[\w]+ flg=0x[\d]+ }\nBroadcast completed: result=(?P<result>[\d]+).", re.DOTALL)

def cmd_res(cmd):
    p = subprocess.Popen([arg for arg in str(cmd).split()], stdin=subprocess.PIPE)
    p.wait()
    if p.returncode == 0:
        return 0
    else:
        return 1
for i in range(1, iterations+1):
    print("Starting iteration {}".format(i))
    for j in range(1, num_devs+1):
        print("starting uploader on device id={}".format(j))
        stat = cmd_res(prefix.format("CONNECT_ACCESSORY --ei id {}").format(j))
        if stat == 0:
            stat = cmd_res(prefix.format("START_TEST_BULKCLIENT --ei id {} --ei category 11").format(j))
            if stat == 0:
                if j <= num_devs:
                    sleep(1)
                    _ = input("hit enter when ready for next iteration...")
        else:
            print("Error iteration {}".format(i))
print("finished!")
