import csv
from surveyDI_conf import logger, Globals
import os
from sys import exc_info
from traceback import format_exception
from MySQLdb import connect


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
    logger.error("{}: {}.\n Check log file for details".format(etype, value))
    logger.debug(''.join(format_exception(etype, value, tb)))
    if message:
        logger.debug(message)
    if not Globals.PROBLEMS:
        Globals.PROBLEMS = 1

def write_to_csv(output_file, headers, values_list, delim='\t'):
    """
    Write header and corresponding values to a csv file
        
    :input: desired output file name
            a list representing the csv file header
            a list of lists, each representing the corresponding values
            delimiter 
    :return: None
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
            

def write_sql_table(cursor, db_name, table_name, headers_list, values_list):
    """
    Write info to an SQL table.

    :input: cursor - MySQLdb cursor object as obtained prior to connecting
                     to the database
            db_name - name of the database to create the table in
            table_name - name of table to be created
            headers_list - table headers
            values_list - list of lists each containing a table row
    :return: None
    :notes: Tables will be dropped and recreated if already exist
    Column names will be the CSV headers with spaces and round
    brackets removed.
    """

    logger.info("\n\tDropping table {}.{}...".format(db_name, table_name))
    cursor.execute("DROP TABLE IF EXISTS {}.{}".format(db_name, table_name))

    logger.info("\tCreating table {}.{}...".format(db_name, table_name))
    db_headers = [x.translate(None, '() ') for x in headers_list]
    create_cmd = "CREATE TABLE {}({})".format(
        table_name,
        ", ".join(["`"+str(x)+"`" + " VARCHAR(3000)" for x in db_headers]))
    cursor.execute(create_cmd)

    logger.info("\tPopulating table {}.{}...".format(db_name, table_name))
    for row in values_list:
        insert_cmd = "INSERT INTO {0}({1}) VALUES({2})".format(
            db_name + "." + table_name,
            ", ".join(["`"+str(x).replace("`", "\\`")+"`" for x in db_headers]),
            ", ".join(["'"+str(x).replace("'", "\\'")+"'" for x in row]))
        try:
            cursor.execute(insert_cmd)
        except Exception as e:
            if len(db_headers) != len(row):
                write_exception('''
Different sizes in header ({}) and row ({}): 
header:{}
row:   {}'''.format(len(db_headers), len(row), db_headers, row))
            else:
                write_exception("SQL error while executing command:\n\t{}".format(insert_cmd))
            return


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
    def __init__(self, id, text, fileid, order):
        self.id = id
        self.text = text
        self.fileid = [fileid]
        self.order = [order]

    def add_fieldid(self, fileid):
        self.fileid.append(fileid)

    def add_order(self, order):
        self.order.append(order)
    
    def __str__(self):
        return "{} {} {}".format(self.id, self.fileid, self.text)


class Parser():
    def __init__(self, input_dir):
        self.input_dir = input_dir
        #surveys
        self.surveys = []
        self.fheader = ["SurveyID", "Filename"]  
        self.stable = "Surveys"
        #questions
        self.questions = []
        self.qheader = ["QuestionID", "QuestionText"]
        self.qtable = "Questions"
        #surveyquestions
        self.squestions = []
        self.sqheader = ["SurveyID", "QuestionID", "QuestionOrder"]
        self.sqtable = "SurveysQuestions"
        #respondents
        self.respondents = []
        self.rheader = ["SurveyID", "RespondentID", "CollectorID", "StartDate", "EndDate", "IP Address", "Email Address", "First Name", "LastName", "Custom Data"]
        self.rtable = "Respondents"
        #questionresponses
        self.qresponses = []
        self.qrheader = ["QuestionID", "RespondentID", "Response"]
        self.qrtable = "QuestionResponses"

    def get_question_by_text(self, text):
        for q in self.questions:
            if q.text == text:
                return q

    def get_surveys(self):
        if not self.surveys:
            survey_list = get_csv_files(self.input_dir)
            self.surveys = [InputFile(id+1, name) for id, name in enumerate(survey_list)]
            logger.info("Surveys found: {}".format(len(self.surveys)))
            for survey in self.surveys:
                logger.info("\t--> {}.{}".format(survey.id, survey.name))
        
    def get_questions(self):
        if not self.questions:
            all_questions_list = []
            questions_delim = "Custom Data"
            self.get_surveys()
            for input_file in self.surveys:
                try:
                    with open(input_file.name, 'rb') as csv_file:
                        fileid = input_file.get_id()
                        reader = csv.reader(csv_file)
                        headers = reader.next()
                        qstart_idx = headers.index(questions_delim) + 1
                        #get questions 
                        qlist = headers[qstart_idx:]
                        all_questions_list.extend([(text, fileid, qorder+1) 
                                                   for qorder, text in enumerate(qlist)])
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
                    (qtext, qfileid, qorder) = info
                    if qtext == text:
                        all_questions_list.remove(info)
                        if not q:
                            q = Question(id+1, qtext, qfileid, qorder)
                            self.questions.append(q)
                        else:
                            q.add_fieldid(qfileid)
                            q.add_order(qorder)
            logger.info("Distinct questions found: {} (total {})".format(
                    len(self.questions), total))
        
    def get_surveyquestions(self):
        self.get_questions()
        for q in self.questions:
            for fileid in q.fileid:
                for order in q.order:
                    self.squestions.extend([(fileid, q.id, str(fileid)+"-"+str(order))])
           
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
                        questions = headers[qstart_idx:]
                        for row in reader:
                            # process respondents
                            user_details = row[:qstart_idx]
                            user_details.insert(0, fileid)
                            self.respondents.append(user_details)
                            # process responses
                            user_responses = row[qstart_idx:]
                            user_id = user_details[1]
                            for qtext, response in zip(questions, user_responses):
                                q = self.get_question_by_text(qtext)
                                self.qresponses.append((q.id, user_id, response))            
                except:
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
        self.get_surveyquestions()
        write_to_csv(output_file, self.sqheader, self.squestions)

    def write_respondents(self, output_file):
        self.get_respondents()
        write_to_csv(output_file, self.rheader, self.respondents)

    def write_responses(self, output_file):
        self.get_respondents()
        write_to_csv(output_file, self.qrheader, self.qresponses)

    def write_all_to_mysql(self, server_name, user, passw, db_name):
        logger.info("Writing do database {}:".format(db_name))
        conn = connect(server_name, user, passw, db_name)
        with conn:
            cur = conn.cursor()
            # surveys
            write_sql_table(cur, db_name, self.stable, self.fheader, 
                            [(s.id, s.name) for s in self.surveys])            
            # questions
            write_sql_table(cur, db_name, self.qtable, self.qheader,
                            [(q.id, q.text) for q in self.questions])
            # surveyquestions
            write_sql_table(cur, db_name, self.sqtable, self.sqheader, self.squestions)
            # respondents
            write_sql_table(cur, db_name, self.rtable, self.rheader, self.respondents)            
            # responses
            write_sql_table(cur, db_name, self.qrtable, self.qrheader, self.qresponses)


