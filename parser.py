# This script takes in a text file as an input and parses that text using the re library. Two types of text files are expectd:
# 1- request acknowledgement
# 2- request confirmation
# 3- the text is parsed into key, value pairs, and sent as a Json object to a webhook where subsequent action is taken.
import re
import requests
import json
import pandas as pd

# Parse the text file into key, value pairs.
def parse(line):
    # Parsing the Confirmation Number
    confirmation = re.findall(r"Conf.*[Nn][ou].*:.*", line)
    if confirmation:
        return 'confirmation no', confirmation[0].split(':')[1].strip()
    
    # Parsing the Assignement Data
    assignment_date = re.findall(r"Assign.*[Dd]ate ?:.*[2][\d]{3}", line)
    if assignment_date:
        return 'assignment date', ':'.join(assignment_date[0].split(':')[1:]).strip()  #assignment_date[0].split(':')[1].strip()

    # Parsing the Assignement Time
    assignment_time = re.findall(r"Assign.*[T]?[t]?ime ?:.*", line)
    if assignment_time:
        return 'assignment time', ':'.join(assignment_time[0].split(':')[1:]).strip()

    # Parsing the Requester Name
    requested_by = re.findall(r"Req.*[Bb]y.*:*", line)
    if requested_by:
        return 'requested by', requested_by[0].split(':')[1].strip()

    # Parsing the interpreted language
    language = re.findall(r"[Ll]ang.*:.*", line)
    if language:
        return 'language', language[0].split(':')[1].strip()

    # Parsing the Request Number
    request_number = re.findall(r"[Rr]eq.* [Nn][ou].*:.*[\d]*", line)
    if request_number:
        return 'request number', request_number[0].split(':')[1].strip()

    # Parsing the Location
    location = re.findall(r"[Ll]oc.*:.*", line)
    if location:
        return 'location', location[0].split(':')[1].strip()

    # Parsing the Assignement Interpreter
    assigned_interpreter = re.findall(r"[Aa]ssig.* [Ii]nterp.*:.*", line)
    if assigned_interpreter:
        return 'assigned interpreter', assigned_interpreter[0].split(':')[1].strip()

    # Determining if the request is confirmed
    status_conf = re.findall(r"[Tt]his is.*[Cc]onfirma.*", line)
    if status_conf:
        return 'status', 'confirmed'
    
    # Determining if the request is entered
    status_ent = re.findall(r"[Ww]e have entered", line)
    if status_ent:
        return 'status', 'entered'

if __name__ == '__main__':
    webhook = input('Please enter your webhook url and hit ENTER: ')
    
    # Open the text file nad create template dictionary
    with open(r"ATPWed, 10 Jun 2020 15_37_11 +0000.txt", 'r') as email:
        dict_ = {
            'status'                    : 'other',
            'confirmation no'           : '',
            'assignment date'           : '',
            'assignment time'           : '',
            'company'                   : "Boston Children's Hospital",
            'requested by'              : '',
            'language'                  : '',
            'request number'            : '',
            'location'                  : '',
            'assigned interpreter'      : 'TBD',
            'content'                   : ''
        }
        # Update the dictionary according to parse() function 
        while True:
            line = email.readline()
            if not line:
                break
            try:
                key, value = parse(line)
                dict_[key] = value
            except:
                dict_['content'] += line
            finally:
                dict_['content'] += line

        if dict_['status'] != 'other':
            dict_['content'] = ''
        else:
            dict_ = {'status': 'other', 'content' : dict_['content']}
    
    # Create the Json object, and post it to the webhook
    json_object = json.dumps(dict_)
    requests.post(webhook, data = json_object)
    print('Object sent successfully!')
