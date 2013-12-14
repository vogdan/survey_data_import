import csv
from surveyDI_conf import logger
import os


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
    
    logger.info("\tWriting file {}...".format(output_file))
    with open(output_file, 'wb') as csv_file:
        writer = csv.writer(csv_file, delimiter=delim)
        writer.writerow(headers)
        for values in values_list:
            writer.writerow(values)



class InputFile():
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_id(self):
        return self.id

    def get_filename(self):
        return os.path.basename(self.name)
    
    def __str__(self):
        print "{} {}".format(self.id, self.name)


class Question():
    def __init__(self, id, text, fileid):
        self.id = id
        self.text = text
        self.fileid = [fileid]

    def add_fieldid(self, fileid):
        self.fileid.append(fileid)


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

    def get_question(self, text):
        for q in self.questions:
            if q.text == text:
                return q
        return None

    def get_surveys(self):
        if not self.surveys:
            survey_list = get_csv_files(self.input_dir)
            self.surveys = [InputFile(id+1, name) for id, name in enumerate(survey_list)]
            logger.info("\tSurveys found: {}".format(len(self.surveys)))
        
    def get_questions(self):
        if not self.questions:
            questions_list = []
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
                        questions_list.extend([text for text in headers[qstart_idx:]
                                              if text not in questions_list])
                        all_questions_list.extend([(text, fileid) 
                                                   for text in headers[qstart_idx:]])
                except IOError as e:
                    logger.error("Cannot read file '{}'".format(input_file))
                    logger.debug("Exception:\n{}".format(e))
            logger.info("unq questions {}".format(len(questions_list)))
            logger.info("all questions {}".format(len(all_questions_list)))

            # info is a tuple: (question_text, file_id)
            # !!! Question 49 must be in both
            for id, text in enumerate(questions_list):
                q = self.get_question(text)
                if q:
                    for info in all_questions_list:
                        if info[0] == text:
                            all_questions_list.remove(info)
                            q.add_fieldid(info[1])
                else:
                    for info in all_questions_list:
                        if info[0] == text:
                            all_questions_list.remove(info)
                            self.questions.append(Question(id+1, text, info[1]))
                            
            logger.info("\tDistinct questions found: {}".format(len(self.questions)))
                        
                              
    def write_surveys(self, output_file):
        self.get_surveys()
        survey_list = [(survey.id, survey.get_filename()) for survey in self.surveys]
        write_to_csv(output_file, self.fheader, survey_list)
    
    def write_questions(self, output_file):
        self.get_questions()
        questions_list = [(question.id, question.text) for question in self.questions]
        write_to_csv(output_file, self.qheader, questions_list)
    
    def write_surveysquestions(self, output_file):
        self.get_questions()
        sq_list = [(question.fileid, question.id) for question in self.questions]
        write_to_csv(output_file, self.sqheader, sq_list)
