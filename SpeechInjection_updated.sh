#!/bin/bash
#Written by Daniel Bressman

#sudo ./SpeechInjection_plus.sh <TX> <RX> <both> 
#Todo:
#automate gestures using serial commands

adb root
adb remount

RXcommand="alexa, ask twinkle band to play animation 1"
TXcommand="alexa, ask twinkle band to start listening for gestures"

if [ "$1" == "" ]; then
	echo "USAGE: $0 \"Alexa, what time is it\""
	exit 1
fi

if [[ "$1" == "RX" ]]; then
	count=0
	for i in $(seq 1 100);
	do
		timestamp=`date +%H:%M:%S`
		count=$((count+1))
		echo ""
		echo "********Iteration $count @ $timestamp**********"
		echo ""
		adb shell am startservice -n com.amazon.knight.test.support/.SpeechInjectorService
		adb shell am broadcast -a amazon.speech.SEND_TO_SIM --es ttsText "\"$RXcommand\""
		sleep 20
	done

elif [[ "$1" == "TX" ]]; then
	count=0
	for i in $(seq 1 33);
	do
		adb shell am startservice -n com.amazon.knight.test.support/.SpeechInjectorService
		adb shell am broadcast -a amazon.speech.SEND_TO_SIM --es ttsText "\"$TXcommand\""
		echo ""
		sleep 10
		for t in $(seq 1 3);
		do
			timestamp=`date +%H:%M:%S`
			count=$((count+1))
			echo "********Iteration $count @ $timestamp**********"
			echo "*****************TAP BANDS NOW*****************"
			echo ""
			sleep 15
		done
		sleep 20
	done

elif [[ "$1" == "both" ]]; then
	count=0
	for i in $(seq 1 100);
  	do
		timestamp=`date +%H:%M:%S`
		count=$((count+1))
		echo ""
		echo "********Iteration $count @ $timestamp**********"
		echo ""
		adb shell am startservice -n com.amazon.knight.test.support/.SpeechInjectorService
		adb shell am broadcast -a amazon.speech.SEND_TO_SIM --es ttsText "\"$RXcommand\""
		sleep 20
	done
	for i in $(seq 1 33);
	do
		adb shell am startservice -n com.amazon.knight.test.support/.SpeechInjectorService
		adb shell am broadcast -a amazon.speech.SEND_TO_SIM --es ttsText "\"$TXcommand\""
		echo ""
		sleep 10
		for t in $(seq 1 3);
		do
			timestamp=`date +%H:%M:%S`
			count=$((count+1))
			echo "********Iteration $count @ $timestamp**********"
			echo "*****************TAP BANDS NOW*****************"
			echo ""
			sleep 15
		done
		sleep 20
	done
fi
