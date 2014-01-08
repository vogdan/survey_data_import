Survey Data Import
==================

Program to convert the CSV files in the input\ directory to a format that can be easily be imported into a database.
Also has options to write data directly to mysql tables corresponding to the output files.


####Usage

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


####Output

Five tab separated files:

```
    QuestionResponses.tab
    Questions.tab
    Respondents.tab
    SurveysQuestions.tab
    Surveys.tab
```



###How To

#####Database setup

   For the database writing to work, we need to create a user and a database and grant all privileges to this user 
   for all tables of the database. 

```mysql
    $ mysql -u root -p
    Enter password: *****
    Welcome to the MySQL monitor.  Commands end with ; or \g.
    Your MySQL connection id is 7
    Server version: 5.6.14 MySQL Community Server (GPL)

    Copyright (c) 2000, 2013, Oracle and/or its affiliates. All rights reserved.

    Oracle is a registered trademark of Oracle Corporation and/or its
    affiliates. Other names may be trademarks of their respective
    owners.

    Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

    mysql> CREATE DATABASE testdb;
    Query OK, 1 row affected (0.02 sec)

    mysql> CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'test623';
    Query OK, 0 rows affected (0.00 sec)

    mysql> USE testdb;
    Database changed

    mysql> GRANT ALL ON testdb.* TO 'testuser'@'localhost';
    Query OK, 0 rows affected (0.00 sec)

    mysql> quit;
    Bye
```


### Specifications

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
- I want to keep track of what order the questions appeared in the survey file. (This is different from the questionID since the same question could appear in multiple surveys in different positions). I think it would make sense to have a new column in SurveyQuestions called QuestionOrder which would be a number 1-n where n is the number of questions in the survey

- It looks like some of the input files from surveymonkey have some duplicated questions in the same survey. This looks like a problem on their end, but we will need to make changes to the code to compensate.
Here's one example: ```Which of the following would you like to see offer customers? (Check all that apply) - Other (please specify)```
Apparently this question is replicated twice in the same survey file. Sometimes the answer to this question is just the last few words of the question ```Other (please specify)``` which is weird.

So here's what I would do: If a question is replicated in the same survey, first look at the answer and if the text is the same as the last few words in the question text, then just ignore that answer text and only use the answer from the other question. If the answer text is different, concatenate the answers.
So there should only be one entry in Questions and one entry in QuestionResponses

For example from the first line of survey 2:
```
Question 1: Which of the following would you like to see offer customers? (Check all that apply) - Other (please specify)
Answer 1: Other (please specify)
Question 2: Which of the following would you like to see offer customers? (Check all that apply) - Other (please specify)
Answer 2: We would like to see a backup person assigned [...]
OUTPUT
Question: Which of the following would you like to see offer customers? (Check all that apply) - Other (please specify)
Answer: We would like to see a backup person assigned [...]
```
