#!/usr/bin/python3

#writen by Cole Sashkin

import logging
import os
import serial
import sys
import time
import threading

logdir = f"{os.getcwd()}/inpark_logs"
if not os.path.exists(logdir):
    os.mkdir(logdir)

logging.basicConfig(format="%(asctime)s - %(module)s - %(levelname)s - %(message)s", filename=f"{logdir}/inpark.log", 
                    filemode="a", level=logging.DEBUG, datefmt="%H:%M:%S")
logger = logging.getLogger()

if len(sys.argv) < 2:
    NUM_DEVS = 1
else:
    NUM_DEVS = int(sys.argv[1])

DEV = "/dev/ttyACM0"
HEAP_CMD = "ace tools sys heap"
TASK_CMD = "ace tools sys task"
CHANGE_INT = 1
ITERATIONS = 1

SLOW_RX = "agt scan set_config 48000 200 4294967295"

FAST_RX = "agt scan set_config 8000 400 10800000"

SLOW_TX_RX_1 = "agt scan set_config 1600 400 1800000"
SLOW_TX_RX_2 = "agt adv set_config 1600 1600 0 0"

FAST_TX_RX_1 = "agt scan set_config 16 16 120000"
FAST_TX_RX_2 = "agt adv set_config 160 160 0 0"

SCAN_START = "agt scan start"
SCAN_STOP = "agt scan stop"
SCAN_CONFIG = "agt scan get_config"
ADV_START = "agt adv start"
ADV_STOP = "agt adv stop"
ADV_CONFIG = "agt adv get_config"


class SerialPort:
    def __init__(self, device, baud, timeout=1):
        self.port = serial.Serial(device, baudrate=baud, timeout=timeout)

    def write_cmd(self, cmd):
        self.port.write("{}\r\n".format(cmd).encode())
        self.port.flush()
        time.sleep(1)

    def read_response(self, size=None):
        res = None
        if not self.port.is_open:
            self.port.open()
        if size is None:
            msg = self.port.readlines()
            res = [str(m.decode()).strip("\r\n") for m in msg]
        elif type(size) == int:
            msg = self.port.read(size)
            res = msg.decode()
        else:
            raise ValueError("size must be an integer or None")
        return res


def mode_generator():
    modes = [[SLOW_RX, SCAN_START, SCAN_CONFIG], 
            [FAST_RX, SCAN_START, SCAN_CONFIG], 
            [SLOW_TX_RX_1, SCAN_START, SCAN_CONFIG, SLOW_TX_RX_2, ADV_START, ADV_CONFIG], 
            [FAST_TX_RX_1, SCAN_START, SCAN_CONFIG, FAST_TX_RX_2, ADV_START, ADV_CONFIG]]
    for mode in modes:
        yield mode

def port_list(num_devs):
    ports = []
    for i in range(num_devs):
        ports.append("/dev/ttyACM{}".format(i))
    return ports


def handle_port(dev):
    p = SerialPort(dev, 115200)
    stat_cmds1 = [SCAN_STOP, HEAP_CMD, TASK_CMD]
    stat_cmds2 = [SCAN_STOP, ADV_STOP, HEAP_CMD, TASK_CMD]
    i = 0
    while True:
        if i >= ITERATIONS:
            break
        try:
            t1 = time.perf_counter()
            for mode in mode_generator():
                logger.debug(f"starting mode {mode} on dev {dev}")
                for m in mode:
                    p.write_cmd(m)
                time.sleep(CHANGE_INT)
                if len(mode) > 3:
                    stat_cmds = stat_cmds2
                else:
                    stat_cmds = stat_cmds1
                for c in stat_cmds:
                    p.write_cmd(c)
            t2 = time.perf_counter()
            t = t2 - t1
            logger.debug("iteration: {} perf_time: {}s".format(i, t))
            i += 1
        except KeyboardInterrupt:
            break
    if p.port.isOpen():
        p.port.close()

def main():
    threads = []
    ports = port_list(NUM_DEVS)
    for i, port in enumerate(ports):
        try:
            t = threading.Thread(target=handle_port, args=[port], name=f"dev_{i}")
            threads.append(t)
            t.start()
            logger.debug(f"starting thread for port {port}")
        except KeyboardInterrupt:
            break
    for thread in threads:
        logger.debug(f"waiting for thread {thread.name}...")
        thread.join()
        logger.debug(f"{thread.name} if finished!")

if __name__ == "__main__":
    main()