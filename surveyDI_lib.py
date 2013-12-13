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
        self.fileid = []

    def set_fieldid(self, fileid):
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

    def get_surveys(self):
        survey_list = get_csv_files(self.input_dir)
        self.surveys = [InputFile(id+1, name) for id, name in enumerate(survey_list)]
        
    def get_questions(self):
        """
        Get info for the "Questions.tab" output file
        
        :input: input_files - list of InputFile instances
                output_file - the name of the file containing the questions
        :output: 
        """
        questions_list = []
        if not self.surveys:
            self.get_surveys()
        for input_file in self.surveys:
            questions_delim = "Custom Data"
            try:
                with open(input_file.name, 'rb') as csv_file:
                    file_id = input_file.get_id()
                    reader = csv.reader(csv_file)
                    headers = reader.next()
                    qstart_idx = headers.index(questions_delim) + 1
                    questions_list.extend([x for x in headers[qstart_idx:] 
                                      if x not in questions_list])
            except IOError as e:
                logger.error("Cannot read file '{}'".format(input_file))
                logger.debug("Exception:\n{}".format(e))
        self.questions = [Question(id+1, text, file_id) 
                          for id, text in enumerate(questions_list)]

    def write_surveys(self, output_file):
        if not self.surveys:
            self.get_surveys()
        survey_list = [(survey.id, survey.get_filename()) for survey in self.surveys]
        write_to_csv(output_file, self.fheader, survey_list)
    
    def write_questions(self, output_file):
        if not self.questions:
            self.get_questions()
        questions_list = [(question.id, question.text) for question in self.questions]
        write_to_csv(output_file, self.qheader, questions_list)
    

