#!/usr/bin/python3

#written by Cole Sashkin

import subprocess
import sys
import threading
from time import sleep

if len(sys.argv) < 4:
    print(f"Usage: {__file__} <num_devices> <framesize> <total_bytes> [iterations] [test_type]")

num_devs = int(sys.argv[1])
frame_size = int(sys.argv[2])
total_bytes = int(sys.argv[3]) 

iterations = None
test_type = "concurrent"

if len(sys.argv) >= 5:
    iterations = int(sys.argv[4])
    if len(sys.argv) == 6:
        test_type = str(sys.argv[5])


CMD = "adb shell am broadcast -a com.amazon.amatest.STRESS_DATA --ei id {} --ei framesize {} --ei datasize {}"

def run_stress_data(i):
    subprocess.call(CMD.format(i, frame_size, total_bytes), shell=True)
    sleep(0.5)

def concurrent_stress_test(n):
    threads = []
    for i in range(1, n+1):
        t = threading.Thread(target=run_stress_data, args=[i])
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    
def serial_stress_data_ctrl(n):
    for i in range(1, n+1):
        subprocess.call(CMD.format(i, frame_size, total_bytes), shell=True)
        _ = input("Hit Enter when ready to continue...")

def multi_iter_test(test_type, iterations=None):
    if str(test_type).lower() in {"serial", "serially", "sequential"}:
        func = serial_stress_data_ctrl
        test_type = "serial"
    elif str(test_type).lower() in {"concurrent", "concurrently", "parallel"}:
        func = concurrent_stress_test
        test_type = "concurrent"
    if iterations is not None:
        for _ in range(iterations):
            try:
                func(num_devs)
                if test_type == "concurrent":
                    sleep(110)
                else:
                    continue
            except KeyboardInterrupt:
                break
    else:
        while True:
            try:
                func(num_devs)
                if test_type == "concurrent":
                    sleep(110)
                else:
                    continue
            except KeyboardInterrupt:
                break

multi_iter_test(test_type, iterations=iterations)