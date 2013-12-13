#!/usr/bin/env python

from argparse import ArgumentParser
from time import gmtime, strftime
import os
import surveyDI_lib
from surveyDI_conf import logger, LOG_FILE_PATH, LOG_FILE
from surveyDI_conf import OPUT_QR, OPUT_SQ, OPUT_Q, OPUT_R, OPUT_S


def parse_cli_opts():
    global args

    arg_parser = ArgumentParser(description='''convert the CSV files in the input\ 
directory to a format that can be easily be imported into a database''')
    arg_parser.add_argument('-i', '--input_dir', 
                        help='Directory containing input csv files', 
                        required=True)
    arg_parser.add_argument('-o', '--output_dir', 
                        help='Directory that will contain output files', 
                        default=".")
    args = arg_parser.parse_args()


def main():
    global args

    parse_cli_opts()
 
    file_parser = surveyDI_lib.Parser(args.input_dir)
    output_file = 'Surveys.tab'
    file_parser.write_surveys(output_file)
    output_file = 'Questions.tab'
    file_parser.write_questions(output_file)
    output_file = 'SurveysQuestions.tab'
    file_parser.write_surveysquestions(output_file)

if __name__ == "__main__":
    log_delimiter = "#"*20 + strftime("%a, %d %b %Y %X +0000", gmtime()) + "#"*10
    logger.debug("\n"*2 + log_delimiter + "\n") 

    main()

    print "\nDebug log: '{}'\n".format(os.path.join(LOG_FILE_PATH, LOG_FILE))
