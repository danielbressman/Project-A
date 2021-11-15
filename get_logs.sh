#! /bin/bash

#written by Daniel Bressman

mkdir -p /home/danielbressman/Desktop/logs/"Logs_$(date)";
cd "Logs_$(date)"
adb pull /data/misc/bluedroid/ ./"$(date)_bluedroid_logs"
adb pull /data/misc/bluetooth/logs ./"$(date)_bluetooth-snoop_log"
adb pull /sdcard/btsnoop_hci.log ./"$(date)_bluetooth-snoop_log"
adb pull /data/misc/blemesh ./"$(date)_blemesh"
adb pull /data/tombstones ./"$(date)_tombstones"
adb pull /data/misc/ama/ama.bin ./"$(date)_ama"
adb pull /data/misc/bluedroid/bt_config.conf ./"$(date)_bt_config"


