#!/usr/bin/python3
###############################################################################
#               Author: Ciaran Maher                                          #
#               Email:  ciaranmaher@gmail.com                                 #
#               Date:   27/07/2021                                            #
###############################################################################
# Todo:
# Refactor to use Structure(object) class
#   Include type enforcement in class
#   Validation on xml input file
# Refactor to streamlined methods
# Refactor away from Regex.
# Refactor away from grouper(list, 2) for getting file paths
# Refactor try/except block for parsing different timestamp formats
# Build custom JSON Encoder to support seriliasing timestamp
# Add parameter to allow overwrite or append JSON output files
# Assumptions
# 1) Script is expected to run on a *nix host
# theoretically should work on Windows environment but untested
# might require some minor tweaks
# 2) For ID creation, I assumed that a combination of job_number + "_" +
# str(suite_start_time) + "_" + j['testName'] would be sufficient to provide a
# reproducible but unique ID. The ID is only reproducible while using this
# script or similar to calculate the start time of each testcase and combine it
# with the other known values.
# 3) Assumed 4489 run.properties is malformed. Error is caught but forces
# script exit. Assumed that malformed property files are threat to data
# integrity. Would like another pass at this feature however.
# 4) All python libraries are available for script execution.
# 5) Ugly working code is better than slick broken code. Would have preferred
# to use own structure class to type check all parameters to ensure data
# integrity ala Python Cookbook.
# 6) I did not get a chance to spin-up my own instance of elasticsearch to
# consume the json generated here. The wording of the assignment implied that
# there might be other required target fields that were not mentioned. In
# addition, I am not familiar enough with Elasticsearch yet to confirm if all
# fields are searchable.
# 7) Ran out of time while trying to research and develop a custom JSONencoder
# to serialise timestamp format. Went with the quicker option to create a
# timestamp as a string using the ISO 8601 format.
# standard python modules
import getopt
import os
import sys
import json
import re
from datetime import datetime
from itertools import zip_longest

# non-standard python modules
# pip install xmltodict
import xmltodict
# pip install jproperties
from jproperties import Properties

# Default parameter for output. As it is not a required parameter, this will
# default to print JSON to stdout if no path is specified.
output = 'stdout'
# Debugging parameter, to turn on outputs while developing/troubleshooting
verbose = False


def grouper(iterable, n, fillvalue=None):
    # Helper method, provided by itertools recipes. Included to remove the need
    # for additional module. Used to split file_list into xml and property
    # pairs.
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def print_results(xml, properties):
    # Primary method for the script. Should be refactored into multiple
    # separated methods. Takes a relative path to xml and the properties file
    configs = Properties()
    if verbose:
        print (f"Property value is: {properties}")
    # On call the method loads the first properties file and tries to find the
    # expected properties. Failure to find these properties terminates the
    # script to ensure data integrity.
    with open(properties, 'rb') as config_file:
        configs.load(config_file)
    config_file.close()
    try:
        revision = configs.get("revision").data
        runtype = configs.get("runtype").data
        brand = configs.get("brand").data
        category = configs.get("category").data
        job_name = configs.get("job_name").data
    except:
        print(f"Could not access all expected properties.")
        sys.exit(3)
    if verbose:
        print (f"Xml value is: {xml}")
    # Likewise, loads the xml file and uses xmltodict module to parse to a
    # python dictionary.
    with open(xml) as xml_file:
        data_dict = xmltodict.parse(
            xml_file.read(), process_namespaces=True
        )
    xml_file.close()
    # Greedy regexp to find the subdirectory where the xml was found.
    # Used to find the Job Number. Potential risk of breakage and I
    # don't like regexp as a general rule. Needs another pass.
    job_number = re.findall(".*\/([^\/]+)\/", xml)[0]
    # If there is only one suite in our xml then we will have trouble with
    # this algorithm. As a result, checks to see if this element is already a
    # list of suites and if not, it converts it to a list of one value.
    if not isinstance(data_dict['result']['suites']['suite'], list):
        data_dict['result']['suites']['suite'] = [
                                                    data_dict['result']
                                                    ['suites']['suite']
                                                    ]
    # Iterate through our list of suites to begin parsing data
    for k in data_dict['result']['suites']['suite']:
        # Hacky workaround for the differences in timestamp format between some
        # test results. Not happy with this, but functional. Needs another pass
        # Initialises the suite start time based on the precision of the
        # timestamp
        try:
            suite_start_time = datetime.strptime(
                                                k['timestamp'],
                                                "%Y-%m-%dT%H:%M:%S"
                                                ).timestamp()
        except ValueError:
            suite_start_time = datetime.strptime(
                                                k['timestamp'],
                                                "%Y-%m-%dT%H:%M:%S.%f"
                                                ).timestamp()
        # Similar to suites, casts the case to a list, in case of single case
        if not isinstance(k['cases']['case'], list):
            k['cases']['case'] = [k['cases']['case']]
        # Iterates through all cases in our xml
        for j in k['cases']['case']:
            temp_dict = {}
            # Build a temporary dictionary with all the values we need
            temp_dict['job_number'] = int(job_number)
            temp_dict['brand'] = brand
            temp_dict['revision'] = int(revision)
            temp_dict['runtype'] = runtype
            temp_dict['category'] = category
            temp_dict['job_name'] = job_name
            temp_dict['file'] = k['file']
            temp_dict['name'] = k['name']
            temp_dict['timestamp'] = k['timestamp']
            temp_dict['classname'] = j['className']
            temp_dict['testname'] = j['testName']
            temp_dict['duration'] = float(j['duration'])
            # Convert string boolean to actual boolean
            if j['skipped'] == "true":
                temp_dict['skipped'] = True
            else:
                temp_dict['skipped'] = False
            # Simple logic check to create the "passed" custom field
            # and add errorStackTrace field if appropriate
            if int(j['failedSince']) == 0:
                temp_dict['passed'] = True
            else:
                temp_dict['passed'] = False
                if j['skipped'] != "true":
                    temp_dict['errorStackTrace'] = j['errorStackTrace']
            temp_dict['starttime'] = datetime.fromtimestamp(suite_start_time)
            suite_start_time += float(j['duration'])
            # Build our unique, reproducible string ID custom field
            temp_dict['id'] = job_number + "_" + str(suite_start_time) \
                + "_" + j['testName']
            temp_dict['stdout'] = k['stdout']
            temp_dict['stderr'] = k['stderr']
            # Dump our whole temporary dictionary to JSON using a default
            # string encoder for unhandled datatypes. Forces timestamp fields
            # to be ISO 8601 format, but not quite what the assignment requires
            # Needs another pass.
            json_data = json.dumps(temp_dict, default=str)
            # If an output parameter is specified, then check if directory
            # exists and if so, output the json to the location. Assumed that
            # appending existing JSON was better than deleting existing files,
            # but may be better to throw an error or take a parameter to
            # append or overwrite. Needs another pass.
            if output == "stdout":
                print(json_data)
            elif os.path.isdir(output):
                save_path = output + "/" + job_name + \
                            "_" + job_number + ".json"
                with open(save_path, "a") as json_file:
                    json_file.write(json_data)
                    json_file.write("\n")
                json_file.close()
            else:
                print("Invalid output directory.")
                print(f"Please ensure that {output} "
                      "is a valid directory before using this script.")
                print("./pico_test_print.py -d <path/to/files>"
                      "-o <path/to/output>")
                print("e.g. ./pico_test_print.py -d dataset1/"
                      "-o .")
                sys.exit()


def main(argv):
    global output, verbose
    try:
        opts, args = getopt.getopt(argv, "hd:o:v", [
                                                    "directory=", "output=",
                                                    "verbose="
                                                    ])
    except getopt.GetoptError:
        print('Invalid script usage. Correct usage is:')
        print('pico_test_print.py -d <path/to/files> -o <output type>')
        print('e.g.\npico_test_print.py -d <dataset1/> -o json')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Script written by Ciaran Maher')
            print('ciaranmaher@gmail.com')
            print('pico_test_print.py -d <path/to/files> -o <path/to/output>')
            print('e.g. ./pico_test_print.py -d dataset1/ -o .')
            sys.exit()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
            print ('Working directory is: ' + directory)
            print('Print results to: ' + output)
    # Build a list of all folders with xml and properties files, recursively
    # using os.walk
    file_list = []
    for root, directories, files in os.walk(directory, topdown=True):
        for name in files:
            if name.endswith('.xml'):
                file_list.append(os.path.join(root, name))
            if name.endswith('.properties'):
                file_list.append(os.path.join(root, name))
    # Had some issues building a reliable way to match xml and properties file
    # locations together. This was the first approach that did what I wanted,
    # but in hindsight there are obvious risks here. If an xml or properties
    # file is missing, then this will cause issues without drawing immediate
    # attention to the cause. Needs another pass.
    tup = grouper(file_list, 2)
    for k, v in tup:
        print_results(k, v)


if __name__ == "__main__":
    main(sys.argv[1:])
