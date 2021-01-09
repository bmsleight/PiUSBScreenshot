#!/usr/bin/env python
""" piusb - get screenshot of website presents as usb drive 
Cycles through the config grabs the URLs
Convert to jpg
umount usb mass_storage
transferes them to usb
remounts mass_storage
"""

import configparser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from datetime import datetime  
from datetime import timedelta  

import os
import tempfile
import sys
import time

__author__ = "Brendan Sleight"
__license__ = "MIT"

CONFIGINI = "/home/pi/piusb.ini"
MNT = "/media/piUSBshared/"

def log(text):
	log = (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " piUSB " +
			text)
	print(log)
	
def mountMS():
	log("mount MS")
	os.system('sync; sudo modprobe g_mass_storage file=//dev/mmcblk0p3 stall=0 ro=1')

def umountMS():
	log("umount MS")
	os.system('sudo modprobe -r g_mass_storage')

def showConnecting():
	umountMS()
	os.system('rm ' + MNT + '*.jpg')
	os.system('convert -size 800x600 xc:white  -pointsize 72 -gravity center  -draw "text 0,0 \'Connecting ...\'" ' + MNT + 'wait.jpg')
	mountMS()

def setWireless(ssid, password):
	#os.system('sudo ls')
	log(ssid + password)

def setUpChrome(x, y):
	options = webdriver.chrome.options.Options()
	options.headless = True
	options.add_argument('--window-size='+ str(x) + ',' + str(y) )
	chrome = webdriver.Chrome(options=options)
	return chrome

def getScreenshots(tempdirname, urls, x, y):
	i = 1
	chrome = setUpChrome(x, y)
	for url in urls:
		png = tempdirname + "/" + str(i) + ".png" 
		log("Get " + url + " as " + png)
		chrome.get(url)
		chrome.save_screenshot(png)
		log("Png saved :" + png)
		i += 1
	chrome.close()	

def convertScreenshots(tempdirname):
	os.system('mogrify -format jpg ' + tempdirname + '/*.*')

def umountCopyRemount(tempdirname):
	log('unmount copy remount')
	umountMS()
	os.system('rm ' + MNT + '*.jpg')
	os.system('cp ' + tempdirname + '/*.jpg ' + MNT)
	mountMS()

def waitUntil(start, seconds):
	end = start + timedelta(seconds=int(seconds))
	log("Wait until end - " + end.strftime("%Y-%m-%d %H:%M:%S"))
	while True:
		diff = (end - datetime.now()).total_seconds()
		if diff < 0: 
			return 
		time.sleep(diff/2)
		if diff <= 0.1: 
			return

if __name__ == '__main__':    
	config = configparser.ConfigParser()
	config.read(CONFIGINI)
	ssid = config['WIRELESS']['SSID']
	password = config['WIRELESS']['Password']
	x = config['BROWSER']['x']
	y = config['BROWSER']['y']
	seconds = config['BROWSER']['Minimal_Seconds']

	urls = config['BROWSER']['urls'].split('\n')
	urls.remove('')
	tempdir = tempfile.TemporaryDirectory(prefix="piUSB2")	
	
	showConnecting()
	
	setWireless(ssid, password)
	start = datetime.now()  
	
	log("start")
	while True:
		log("Running screenshots ....")
		getScreenshots(tempdir.name, urls, x, y)
		log("Coverting screenshots ....")
		convertScreenshots(tempdir.name)
		waitUntil(start, seconds)
		start = datetime.now()
		umountCopyRemount(tempdir.name)
	
	log("Completed")

	tempdir.cleanup()
