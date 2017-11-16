'''

Author: Sang-tak Lee
Contact: chst27@gmail.com
Version: 1.0
Date: 06/30/2014
Last Update: 


Description:
This module is for log in maya.
I can say simple version of the logging module for using in maya.

You can print out infotmation what you want to see.

Create logger object. 
Set level. 

e.g.
-----------------------------------------
import tak_logging
reload(tak_logging)

# creat logger
logger = tak_logging.Logger()
# set level
logger.setLevel('WARNING')

def logTest():
	logger.debug('debug message')
	logger.info('info message')
	logger.warning('warning message')
	logger.error('error message')
	logger.critical('critical message')

logTest()
-----------------------------------------

In this case you will see only the message that higher than warning level.
Because level is set to the WARNING level.

You can use following arguments to set level.
DEBUG
INFO
WARNING
ERROR
CRITICAL

'''


class Logger:
	
	# default level is DEBUG
	level = 10
	
	def setLevel(self, level):
		if level == 'DEBUG':
			self.level = 10
		if level == 'INFO':
			self.level = 20
		if level == 'WARNING':
			self.level = 30
		if level == 'ERROR':
			self.level = 40
		if level == 'CRITICAL':
			self.level = 50
	
	def debug(self, message):
		if self.level <= 10:
			print '# Debug: ' + str(message)
	
	def info(self, message):
		if self.level <= 20:
			print '# Info: ' + str(message)
	
	def warning(self, message):
		if self.level <= 30:
			print '# Warning: ' + str(message)
	
	def error(self, message):
		if self.level <= 40:
			print '# Error: ' + str(message)
	
	def critical(self, message):
		if self.level <= 50:
			print '# Critical: ' + str(message)
