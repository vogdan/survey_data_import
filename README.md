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

Four tab separated files:

```
    QuestionResponses.tab
    Questions.tab
    Responses.tab
    SurveysQuestions.tab
    SurveysQuestions.tab.back
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

