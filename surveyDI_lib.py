import csv
from surveyDI_conf import logger
import os
from sys import exc_info
from traceback import format_exception

def get_csv_files(input_dir, suffix=".csv"):
    """
    Scan the input directory and return a list containing all the .csv files
    found there.
    
    :input: a directory containing input files
            suffix of the input files (by default set to ".csv")
    :return: list containing the csv files in input_dir (full path) 
    """
    
    filenames = os.listdir(input_dir)
    return [os.path.join(input_dir, filename) for filename in filenames 
            if filename.endswith(suffix)]


def read_csv2dict(input_file):
    """
    Read a csv file in a csv reader dictionary
    
    :input: input_file - csv input file
    :return: the csv reader object
    """
   
    logger.info("Reading input file {}".format(input_file))
    with open(input_file) as csv_file:
        reader = csv.DictReader(csv_file)
    return reader


def write_exception(message=None):
    """
    Function to be called after catching an exception.
    Writes exception details to log file and console
    
    :input: message - additional debug message to be written to log
                     (containing vaiable values, or other useful debugging info)
    :return: None
    """    

    etype, value, tb = exc_info()
    logger.error("{}: {}.\n Check log for details".format(etype, value))
    logger.debug(''.join(format_exception(etype, value, tb)))
    if message:
        logger.debug(message)


def write_to_csv(output_file, headers, values_list, delim='\t'):
    """
    Write header and corresponding values to a csv file
        
    :input: desired output file name
            a list representing the csv file header
            a list of lists, each representing the corresponding values
    :return: nothing
    :calling example:
    # write webinar details to csv
            w_info = get_webinar_info(INPUT_FILE)
            write_to_csv(OUTPUT_WEBINARS, w_info[0], [w_info[1]])
    """
    try:
        logger.info("\tWriting file {}...".format(output_file))
        with open(output_file, 'wb') as csv_file:
            writer = csv.writer(csv_file, delimiter=delim)
            writer.writerow(headers)
            for values in values_list:
                writer.writerow(values)
    except:
        write_exception("Trying to write values: {}".format(values))
            

class InputFile():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_id(self):
        return self.id

    def get_filename(self):
        return os.path.basename(self.name)
    
    def __str__(self):
        return "{} {}".format(self.id, self.name)


class Question():
    def __init__(self, id, text, fileid):
        self.id = id
        self.text = text
        self.fileid = [fileid]

    def add_fieldid(self, fileid):
        self.fileid.append(fileid)
    
    def __str__(self):
        return "{} {} {}".format(self.id, self.fileid, self.text)

class Respondent():
    def __init__(self, details, fileid):
        self.details = details
        self.fileid = [fileid]

class Parser():
    def __init__(self, input_dir):
        self.input_dir = input_dir
        #surveys
        self.surveys = []
        self.fheader = ["SurveyID", "Filename"]      
        #questions
        self.questions = []
        self.qheader = ["QuestionID", "QuestionText"]
        #surveyquestions
        self.sqheader = ["SurveyID", "QuestionID"]
        #respondents
        self.respondents = []
        self.rheader = ["SurveyID", "RespondentID", "CollectorID", "StartDate", "EndDate IP Address", "Email Address", "First Name", "LastName", "Custom Data"]
        #questionresponses
        self.qrheader = ["QuestionID", "RespondentID", "Response"]

    def get_question_by_text(self, text):
        for q in self.questions:
            if q.text == text:
                return q
        return None

    def get_surveys(self):
        if not self.surveys:
            survey_list = get_csv_files(self.input_dir)
            self.surveys = [InputFile(id+1, name) for id, name in enumerate(survey_list)]
            logger.info("Surveys found: {}".format(len(self.surveys)))
        
    def get_questions(self):
        if not self.questions:
            all_questions_list = []
            questions_delim = "Custom Data"
            respondents_list = []
            self.get_surveys()
            for input_file in self.surveys:
                try:
                    with open(input_file.name, 'rb') as csv_file:
                        fileid = input_file.get_id()
                        reader = csv.reader(csv_file)
                        headers = reader.next()
                        qstart_idx = headers.index(questions_delim) + 1
                        #get questions 
                        all_questions_list.extend([(text, fileid) 
                                                   for text in headers[qstart_idx:]])
                except IOError as e:
                    write_exception("While reading file '{}'".format(input_file))
                    
            # process questions
            uniq_questions_list = list(set([q[0] for q in all_questions_list]))
            #  get file id for all questions and create questions instances
            #  for each unique question.
            total = len(all_questions_list)
            for id, text in enumerate(uniq_questions_list):
                q = self.get_question_by_text(text)
                for info in all_questions_list:
                    if info[0] == text:
                        all_questions_list.remove(info)
                        if not q:
                            q = Question(id+1, text, info[1])
                            self.questions.append(q)
                        else:
                            q.add_fieldid(info[1])
            logger.info("Distinct questions found: {} (total {})".format(
                    len(self.questions), total))
                   
    def get_respondents(self):
        if not self.respondents:
            questions_delim = "Custom Data"
            self.get_surveys()
            for input_file in self.surveys:
                try:
                    with open(input_file.name, 'rb') as csv_file:
                        fileid = input_file.get_id()
                        reader = csv.reader(csv_file)
                        headers = reader.next()
                        qstart_idx = headers.index(questions_delim) + 1
                        # process respondents
                        for row in reader:
                            user_details = row[:qstart_idx]
                            user_details.insert(0, fileid)
                            self.respondents.append(user_details)
                except exception:
                    write_exception("While reading file '{}'".format(input_file))
            logger.info("Respondents found: {}".format(len(self.respondents)))

    def write_surveys(self, output_file):
        self.get_surveys()
        write_to_csv(output_file, 
                     self.fheader, 
                     [(survey.id, survey.get_filename()) for survey in self.surveys])
    
    def write_questions(self, output_file):
        self.get_questions()
        write_to_csv(output_file, 
                     self.qheader,
                     [(question.id, question.text) for question in self.questions])
    
    def write_surveysquestions(self, output_file):
        self.get_questions()
        print_list = []
        for q in self.questions:
            for fileid in q.fileid:
                print_list.extend([(fileid, q.id)])
        write_to_csv(output_file, self.sqheader, print_list)

    def write_respondents(self, output_file):
        self.get_respondents()
        write_to_csv(output_file, self.rheader, self.respondents)
