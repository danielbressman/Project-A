#!/bin/bash

android7="# Enable BtSnoop logging function
# valid value : true, false
BtSnoopLogOutput=true

# BtSnoop log output file
BtSnoopFileName=/data/misc/bluetooth/logs/btsnoop_hci.log

# Preserve existing BtSnoop log before overwriting
BtSnoopSaveLog=false

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
"

android5="
# Enable BtSnoop logging function
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
"
version=`adb shell getprop ro.build.version.release` || exit
echo "android version: $version"
if echo "$version" | grep -iq "error"; then
  exit
fi

if echo "$version" | grep -iq "^5"; then
  hci_src='/sdcard/'
  config_path='/data/misc/bluedroid/bt_config.xml'
  echo "$android5">bt_stack.conftmp
else
  hci_src='/data/misc/bluetooth/logs/'
  config_path='/data/misc/bluedroid/bt_config.conf'
  echo "$android7">bt_stack.conftmp
fi

devip=$1

if [ -n "$devip" ]; then
    connectdev=`adb connect $devip`
    echo "$connectdev"
    if echo "$connectdev" | grep -iq "Connection timed out"; then
       echo "Is IP ADDR $devip Wrong?"
       exit 1
    fi
fi


echo "adb root"
root_info=`adb root`
echo "$root_info"
if echo "$root_info" | grep -iq "restarting"; then
 sleep 2
fi
echo "adb remount"
remount_info=`adb remount`

echo "$remount_info"
if echo "$remount_info" | grep -iq "dm_verity"; then
  echo "adb disable-verity"
  adb disable-verity&
  wait $!
  echo "adb reboot"
  adb reboot
  echo "***************************************"
  echo "**system rebooting for adb remount  ***"
  echo "***************************************"
  sleep 10
  if [ -n "$devip" ]; then
     count=1
     while [ $count -le 5 ]; do
       connectdev=`adb connect $devip`
       if echo "$connectdev" | grep -iq "Connection timed out"; then
          echo "Connect IP ADDR $devip Again ($count)!"
	  count=$((count + 1))
       else
          break
       fi
     done
  fi

  adb wait-for-device
  echo "adb root"
  adb root
  echo "adb remount"
  adb remount
fi

echo "adb push bt_stack.conf /etc/bluetooth/bt_stack.conf"
adb push bt_stack.conftmp /etc/bluetooth/bt_stack.conf&
wait $!
rm bt_stack.conftmp
echo "adb shell setprop log.tag.ControllerManagerLogs DEBUG"
adb shell setprop log.tag.ControllerManagerLogs DEBUG&
wait $!
echo "adb shell setprop persist.bt.logging true"
adb shell setprop persist.bt.logging true&
wait $!
echo "adb shell setprop persist.bluetooth.stack_logging 6"
adb shell setprop persist.bluetooth.stack_logging 6&
wait $!
echo "adb shell setprop persist.bluetooth.btsnoop_time 1"
adb shell setprop persist.bluetooth.btsnoop_time 1&
wait $!
echo "adb shell setprop persist.bluetooth.btsnoopenable true"
adb shell setprop persist.bluetooth.btsnoopenable true&
wait $!

echo "adb reboot"
adb reboot
echo "***************************************"
echo "**system is rebooting               ***"
echo "***************************************"
adb wait-for-device
echo "***************************************"
echo "**system ready for test now!        ***"
echo "***************************************"
