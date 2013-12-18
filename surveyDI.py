#!/usr/bin/env python

from surveyDI_conf import logger, Globals
import surveyDI_lib
from argparse import ArgumentParser
from time import gmtime, strftime
import os
import sys

def parse_cli_opts():
    global args

    arg_parser = ArgumentParser(description='''convert the CSV files in the input\ 
directory to a format that can be easily be imported into a database''')
    arg_parser.add_argument('-i', '--input_dir', 
                        help='directory containing input csv files', 
                        required=True)
    arg_parser.add_argument('-o', '--output_dir', 
                        help='directory that will contain output files. Will be created if doesn\'t exist')
    arg_parser.add_argument('-d', '--write_to_db',
                        help='write information to database also.',
                        action="store_true")
    arg_parser.add_argument('-D', '--only_to_db',
                        help='only write to database.',
                        action="store_true")
    args = arg_parser.parse_args()


def make_output_path(output_file_name):
    if args.output_dir:
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        return os.path.join(args.output_dir, output_file_name)
    else:
        return output_file_name


def main():
    global args, PROBLEMS
    PROBLEMS = 0

    parse_cli_opts()
 
    file_parser = surveyDI_lib.Parser(args.input_dir)
    
    if not args.only_to_db:
        # Surveys.tab
        file_parser.write_surveys(make_output_path(Globals.OPUT_S))
        # Questions.tab
        file_parser.write_questions(make_output_path(Globals.OPUT_Q))
        # SurveysQuestions.tab
        file_parser.write_surveysquestions(make_output_path(Globals.OPUT_SQ))
        # Respondents.tab
        file_parser.write_respondents(make_output_path(Globals.OPUT_R))
        # QuestionResponses.tab
        file_parser.write_responses(make_output_path(Globals.OPUT_QR))
        # write ro MySQL
        if args.write_to_db:
            file_parser.write_all_to_mysql(Globals.SERVER_NAME, 
                                           Globals.USER, 
                                           Globals.PASS, 
                                           Globals.DB_NAME)
    else:
        logger.info("Writing only to database.")
        file_parser.write_all_to_mysql(Globals.SERVER_NAME, 
                                       Globals.USER, 
                                       Globals.PASS, 
                                       Globals.DB_NAME)


if __name__ == "__main__":
    log_delimiter = "#"*20 + strftime("%a, %d %b %Y %X +0000", gmtime()) + "#"*10
    logger.debug("\n"*2 + log_delimiter + "\n") 
    main()
    if Globals.PROBLEMS:
        print ""
        logger.error("\tProblems detected. Check messages above and log file for details.")
    print "\nDebug log: '{}'\n".format(os.path.join(Globals.LOG_FILE_PATH, 
                                                    Globals.LOG_FILE))
