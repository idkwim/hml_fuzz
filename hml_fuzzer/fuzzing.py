#!/usr/bin/python

from threading import Timer
from winappdbg import *
import shutil
import random
import time
import glob
import os

SEED_DIR = "seeds"
CASE_DIR = "testcases"
CRASH_DIR = "crash"
testcase_path = "" #could be remove no crash mutate files.
gen_flag = False
timer = False
HWP_PATH = r"C:\Program Files\HNC\HOffice9\Bin\Hwp.exe"

def gen_new_testcase():
	global testcase_path, gen_flag, timer
	if gen_flag == False:
		seedlist = glob.glob(SEED_DIR + "/*.hml")
		pickup = random.choice(seedlist)
		now = time.localtime()
		#testcase_path = "testcases/" + "%04d%02d%02d_%02d%02d%02d.hml" %  (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
		testcase_path = "testcases/testcase.hml"
		radamsa_exec = "radamsa.exe " + pickup + " > " + testcase_path

		os.system(radamsa_exec)
		gen_flag = True

def terminator(proc):
	global timer
	timer = False
	try:
		proc.kill()
	except:
		pass

def handle(e):
	global timer, testcase_path
	if e.get_event_code() == win32.EXCEPTION_DEBUG_EVENT and e.is_last_chance():
		timer.cancel()
		timer = False

		crash = Crash(e)
		crash.fetch_extra_data(e)

		data = crash.fullReport(bShowNotes=True)
		shutil.copy(testcase_path, CRASH_DIR + "//" + "%04d%02d%02d_%02d%02d%02d.hml" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec) )

		try:
			e.get_process().kill()
		except:
			pass
	else:
		if not timer:
			timer = Timer(10, terminator, [e.get_process()])
			timer.start()

def fuzzing():
	global testcase_path, gen_flag, timer
	counter = 0

	while True:
		gen_new_testcase()
		print "[+] TRY CASE [%d] " % counter
		timer = False
		debug = Debug(handle, bKillOnExit=True)

		debug.execv([HWP_PATH, os.getcwd() + "\\" + testcase_path], bFollow=True)
		debug.loop()			
		counter += 1
		gen_flag = False

if __name__ == '__main__':
	fuzzing()