import sublime, sublime_plugin, sys
#import json
#import random, os
#from time import gmtime, strftime
from datetime import date, timedelta, datetime
import re

class ReminderFinderCommand(sublime_plugin.TextCommand):

	def run(self, edit, **args):
		print "ReminderFinder Start"

		if args['op'] == 'updateReminders':
			self.updateReminders(edit)

		elif args['op'] == 'addToReminders':
			self.addToReminders(edit)

		elif args['op'] == 'removeFromReminders':
			self.removeFromReminders(edit)

		elif args['op'] == 'sortReminders':
			self.sortReminders(edit)

		elif args['op'] == 'goToReminders':
			self.goToReminders(edit)

		elif args['op'] == 'snooze':
			self.snooze(edit, args)


	def updateReminders(self, edit):

		print "Starting Remind"

		config = sublime.load_settings("Reminder_Finder.sublime-settings")
		
		if type(remindFilePath) is None:
			print "Cannot find correct settings file"
			return

		remindFilePath = config.get("remindFile").encode('ascii','ignore').encode('string-escape')
		insertionFilePath = config.get("todoInsertionFile").encode('ascii','ignore').encode('string-escape')
		startDelim = config.get("startDelimiter").encode('ascii','ignore')
		endDelim = config.get("endDelimiter").encode('ascii','ignore')
		dayLimit = config.get("daysFromNow").encode('ascii','ignore')

		if type(remindFilePath) is None or type(insertionFilePath) is None or type(dayLimit) is None:
			print "Missing Some Settings, Check remindFilePath, insertionFilePath, or dayLimit settings"
			return 

		try:
			f = open(remindFilePath, 'r')
			valid = True
			pass
		except ValueError, IOError:
			valid = False
			print "Cannot open reminder file"

		print "Loaded Reminder File"

		if(valid):
			reminders = f.read().split('\n')
			f.close()

			reminders.sort()

			#Find string of today + dayLimit in "YE-MO-DA" form
			today = date.today()
			endDay = today + timedelta(int(dayLimit))
			endDate = strftime("%Y-%m-%d", endDay.timetuple())

			#print reminders[0]
			#print reminders[0][:10]

			i = 0
			results = ""
			#Loop through sorted list until you run out or until you find a date later than the end date
			while i < len(reminders) and reminders[i][:10] < endDate:
				results += reminders[i]
				results += '\n'
				i+=1

			if not results:
				results = "No reminders within " + endDate + " days\n"

			#Pick up destination File
			try:
				f = open(insertionFilePath.encode('ascii','ignore').encode('string-escape'), 'r')
				valid = True
				pass
			except ValueError, IOError:
				valid = False
				print "Cannot open insertion file"

			print "Loaded Insertion File"

			#Parse through and remove all between start delimiter and end delimiter
			#....also add cases for Start of File and End of File SOF/EOF
			#....also add cases for line numbers of destination file? or relative numbers?
			insert = f.read()
			f.close()
			#print insert

			start = -1
			end = -1
			if startDelim == "sof" or startDelim == "SOF":
				print "Start of File found"
				start = 0
			elif startDelim == "eof" or startDelim == "EOF":
				print "Found Improper startDelim"
				return
			else:
				print "Finding Start Delimiter from String"
				start = insert.find(startDelim) + len(startDelim)

			if endDelim == "eof" or endDelim == "eof":
				print "End of File found"
				end = len(insert)
			elif endDelim == "sof" or endDelim == "SOF":
				print "Found Improper endDelim"
				return
			else:
				print "Finding End Delimiter from String"
				end = insert.find(endDelim)
			
			if start == -1 or end == -1:
				print "Could not find startDelim or endDelim in insertion file"
				return

			#print start
			#print end

			if start != end:
				self.view.erase(edit, sublime.Region(start,end))

			#Insert results into that space
			self.view.insert(edit, start, '\n' +  results)

	def addToReminders(self, edit):
		print "Adding to reminders"

		#grab reminder filename
		config = sublime.load_settings("Handy_Harness.sublime-settings")
		
		remindFilePath = config.get("remindFile").encode('ascii','ignore').encode('string-escape')

		if type(remindFilePath) is None:
			print "Missing Some Settings--Check remindFilePath or insertionFilePath settings"
			return 

		#grab line
		line, start, end = self.grabLine()

		#check if it is a valid reminder, if not valid, do not add to reminders file and do not remove from current file
		if re.match(r"^[0-9]{4}-[0-1][0-9]-[0-3][0-9]", line):		
			try:
				f = open(remindFilePath, 'a')
				valid = True
				pass
			except ValueError, IOError:
				valid = False
				print "Cannot open reminder file"

			print "Loaded Reminder File"

			if valid:
				#append to reminders file
				f.write("\n" + line)
				f.close()

				#if successful, remove from current file
				self.view.erase(edit, sublime.Region(start,end))

				print "Sent {" + line + "} to reminders file"
		else:
			print "Could not find a valid date beginning in the form ####-##-##"

	def removeFromReminders(self,edit):
		##STUB, archive instead of remove?
		print "Removing from Reminders"

		#grab line
		line, start, end = self.grabLine()

		#get info for reminders file
		config = sublime.load_settings("Handy_Harness.sublime-settings")
		
		remindFilePath = config.get("remindFile").encode('ascii','ignore').encode('string-escape')

		if type(remindFilePath) is None:
			print "Missing Some Settings--Check remindFilePath or insertionFilePath settings"
			return -1

		#open reminders file with write permissions
		try:
			f = open(remindFilePath, 'r')
			valid = True
			pass
		except ValueError, IOError:
			valid = False
			print "Cannot open reminder file"
			return -1

		print "Loaded Reminder File"

		#pulling out text from reminders
		reminders = f.read()
		f.close()


		#search for line
		index = reminders.find(line)
		if index == -1:
			print "Could not find that reminder"
			return -1
		else:
			remindEnd = index
			while(remindEnd < len(reminders) and reminders[remindEnd] != '\n'):
				remindEnd += 1

			#erase line from reminders
			if index != 0:
				index -= 1
			elif remindEnd != len(reminders):
				remindEnd += 1

			reminders = reminders[0:index] + reminders[remindEnd:len(reminders)]

			f = open(remindFilePath, 'w')
			f.write(reminders)

			#if successful, remove line from current file
			self.view.erase(edit, sublime.Region(start,end))

		pass

	def goToReminders(self,edit):
		#get info on remind file
		config = sublime.load_settings("Handy_Harness.sublime-settings")
		remindFilePath = config.get("remindFile").encode('ascii','ignore').encode('string-escape')

		#open up a new tab with reminders file
		os.startfile(remindFilePath)
		
		#shift focus to new tab

		pass

	def sortReminders(self,edit):
		#Open up reminders file with write permissions
		config = sublime.load_settings("Handy_Harness.sublime-settings")
		
		remindFilePath = config.get("remindFile").encode('ascii','ignore').encode('string-escape')

		if type(remindFilePath) is None:
			print "Missing Some Settings--Check remindFilePath or insertionFilePath settings"
			return 

		#open reminders file with write permissions
		try:
			f = open(remindFilePath, 'r')
			valid = True
			pass
		except ValueError, IOError:
			valid = False
			print "Cannot open reminder file"

		print "Loaded Reminder File"


		#sort
		reminders = f.read().split('\n')
		f.close()
		
		reminders.sort()

		#insert sorted list back in
		reminders = '\n'.join(reminders)
		f = open(remindFilePath, 'w')
		f.write(reminders)
		f.close()

		pass

	def snooze(self, edit, args):

		#Get line
		line, start, end = self.grabLine()

		#check if valid format
		if not re.match(r"^[0-9]{4}-[0-1][0-9]-[0-3][0-9]", line):
			print "Could not find a valid date beginning in the form ####-##-##"

		else:

			#pull off date, use strptime and strftime to add time to it, put it back  This could be one line, but that's not nice.
			#https://docs.python.org/2/library/datetime.html
			#stub, adding a month adds 4 weeks of days, so a month past 8/15 won't necessarily be 9/15, it might be 9/12 or 9/16 depending on the month lengths.  Feature or bug?..  Consider case 2016-08-15 - Every 15th I do something, then snooze it for a month
			lineDate = line[0:10]
			lineDateStruct = datetime.strptime(lineDate, "%Y-%m-%d")
			newDate = lineDateStruct + timedelta(weeks=args["years"]*52 + args["months"]*4, days=args["days"])
			newDateString = newDate.strftime("%Y-%m-%d")
			newLine = newDateString + line[10:]

			#remove from reminders
			#add to reminders
			#remove from current text


	def grabLine(self):
		s = self.view.sel()[0]

		size = self.view.size()
		start = s.begin()
		end = s.end()

		while(start > 0 and self.view.substr(start - 1) != '\n'):
			start -= 1

		while(end < size and self.view.substr(end) != '\n'):
			end += 1

		return self.view.substr(self.view.full_line(sublime.Region(start,end))).strip().encode('ascii','ignore'), start, end