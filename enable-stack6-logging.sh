#! /bin/bash

#written by Daniel Bressman

adb root
adb remount

echo "adb shell setprop persist.bt.logging true"
adb shell setprop persist.bt.logging true&
wait $!
echo "adb shell setprop persist.bluetooth.stack_logging 6"
adb shell setprop persist.bluetooth.stack_logging 6&
wait $!
echo "adb shell setprop persist.bluetooth.btsnoop_time 1"
adb shell setprop persist.bluetooth.btsnoop_time 1&
wait $!

adb reboot

