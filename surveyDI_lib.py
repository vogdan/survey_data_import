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


def get_surveys(input_dir, output_file):    
    header = ["SurveyID", "Filename"]
    file_list = [(i+1,x) for i,x in enumerate(get_csv_files(input_dir))]
    write_to_csv(output_file, header, file_list)


def get_questions(input_dir, output_file):
    """
    Get info for the "Questions.tab" output file
    
    :input: input_dir - Directory containing input files
    :output: A set containing the questions from all input files (same 
             question in different files will appear onlu once here)
    """

    questions = []

    for input_file in get_csv_files(input_dir):
        questions_delim = "Custom Data"
        output_header = ["QuestionID", "QuestionText"]
        try: 
            with open(input_file, 'rb') as csv_file:
                reader = csv.reader(csv_file)
                headers = reader.next()
                qstart_idx = headers.index(questions_delim) + 1
                questions.extend([x for x in headers[qstart_idx:] 
                                  if x not in questions])
        except IOError as e:
            logger.error("Cannot read file '{}'".format(input_file))
            logger.debug("Exception:\n{}".format(e))

    write_to_csv(output_file, 
                 output_header, 
                 [(i,item) for i,item in enumerate(questions)])
