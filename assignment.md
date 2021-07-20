# Translate from junit xml output to elastic consumable results

The assignment here is to translate from junit xml results to elasticsearch
consumable results.

Our language of choice is python. You may choose a different language.

The purpose here is to see your work. We want to see the reasoning behind doing things - 
reasons for choices, etc.

If you have questions, ask them. If any piece of the assignment is confusing, either
ask for clarification, or state your assumptions in the solution.

All code should be documented to describe what's happening, it's not expected
to be a narrative.

There is some sample data below this folder, you will need to translate it
from the .xml and .properties file into json data that is suitable for
importation into elasticsearch where it will be searchable - all fields
should be searchable.

We need the following items in each test result:

junit results are split into collections of suites, which have a known name. Each suite has a stdout and stderr.
    testsuite has:
        file, name, stdout, stderr, duration, timestamp and time

Each suite is split into one or more testcases, each case has the following information:
    duration, className, testName, skipped, failedSince

In the case of failed/error testcases you will also have:
    errorStackTrace

You can determine if a test has failed by the presence of a non-zero value in the failedSince field.

from the test results themselves we need the following information in every test case result:

file, name, timestamp

From the run properties we need the following information:

brand, revision, runtype, category, job_name

From the foldername, we have the job_number

in every test case we will need the following information:
    duration, className, testName, skipped

You will need to calculate the following pieces of information:
    passed (boolean) - based on the failedSince value being non-zero
    starttime (datetime) - take suite start time, add all prior
        durations of testcases to get an estimated start time
    id - a unique id based on the testcase. This ID should be reproducible

If there are required target fields for the results and they're not
mentioned in these requirements then they'll need to be filled in as
empty.

target elastic document structure:
{
   job_number: integer,
   brand: string,
   revision: integer,
   runtype: string,
   category: string,
   job_name: string,
   file: string,
   name: string,
   timestamp: timestamp,
   classname: string,
   testname: string,
   duration: numeric,
   skipped: boolean,
   passed: boolean,
   starttime: timestamp,
   stdout: string,
   stderr: string,
   id: string
}

Objectives:

Script that:
  - takes a source directory to start from.
  - reads the results in each of the directories found

  - Produce as output new-line delimited json documents for import
      into elasticsearch.

  - Two output choices: stdout or a destination folder

  - Default output is to stdout, and will contain all results for all jobs

  - If you specify a folder to output to, it will produce a series of files,
    with the naming specification: <job_name>_<job_number>.json in that folder
  - The folder would be expected to exist prior to the start of the run

If you're writing python, then:
 - The file should be pep-8 clean

Regardless of the language:
 - The file should be documented
