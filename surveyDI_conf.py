import logging
import sys 
import os


OPUT_QR = "QuestionResponses.tab"
OPUT_SQ = "SurveysQuestions.tab"
OPUT_Q = "Questions.tab"
OPUT_R = "Responses.tab"
OPUT_S = "Surveys.tab"

#####################################################
# Logging HOWTO
# 1. Do not use print. Use the logger object instead by 
#    importing it in your .py file:
#        from config import logger
# 1a. Only use print if you want messages to be displayed
#     at the console but not in the log file
# 2. To log message to console and log file use
#        log.info(message)
# 3. To log message only to log file (debug messages) use     
#        log.debug(message)
# 4. Warning (log.warning )and error (log.error) messages 
#    will be logged to both console and log file.

LOG_FILE = sys.argv[0].split(".")[0] + ".log"
LOG_FILE_PATH = os.getcwd()
logger = logging.getLogger('webinarImport')
logger.setLevel(logging.DEBUG)
# log to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch_format = logging.Formatter('%(levelname)s: %(message)s')
ch.setFormatter(ch_format)
logger.addHandler(ch)
# log to file
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
fh.setFormatter(fh_format)
logger.addHandler(fh)


