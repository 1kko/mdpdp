#!/usr/bin/env python

from pyvirtualdisplay import Display
from selenium import webdriver
import time


def Main(cmd):
	display = Display(visible=0, size=(1280, 1500))
	display.start()

	browser = webdriver.Firefox()
	browser.get('http://localhost/enginediff/report.php')
	# wait for rendering javascript charts.
	time.sleep(2)
	# get text from element_id: "#displaydaterange" to save as filename
	filename=browser.find_element_by_id('displaydaterange').text.replace(' ','').replace('/','')+".png"
	# save screenshot
	browser.save_screenshot(filename)
	# print filename for further use
	print filename
	browser.quit()

	display.stop()
