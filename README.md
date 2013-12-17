survey_data_import
==================

Program to convert the CSV files in the input\ directory to a format that can be easily be imported into a database.


Usage:

    surveyDI.py [-h] -i INPUT_DIR [-o OUTPUT_DIR]
    
    optional arguments:
        -h, --help            Show this help message and exit
        -i INPUT_DIR, --input_dir INPUT_DIR
                              Directory containing input csv files
        -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                              Directory that will contain output files. Will be
                              created if doesn't exist
        -d, --write_to_db     Write information to database also.
        -D, --only_to_db      Only write to database.





Objective:
- Write a python program to convert the files in the input\ directory to a format that can be easily be imported into a database  (see: the files in output\ directory)
- the files in the output directory are mostly complete for the given input files except QuestionResponses.tab only has responses for the first 2 respondents for one of the surveys

Notes:
- the input files are CSV files from surveymonkey
- the output files need to be tab-separated
- the program should be well-documented
- the program should read all files in the input directory and create the output files, overwriting if necessary
- a later program will import the output files into a database

- if multiple surveys have the same question text, that question should only be entered into the Questions file once, with multiple entries in SurveysQuestions

