#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled

import re
import json

def load_response_json(filename):
    """Load a previous created dict from a file"""
    try:
        with open(filename, "r") as response_json:
            response_dict = json.load(response_json)
    except IOError:
        print("Cannot open {}".format(filename))
        return {}

    return response_dict
    
def matched_strings(string1, string2):
    """Return the number of matched words between two strings"""
    number_of_matches = 0
    for string in string1.split(" "):
        if re.search(r'\b{}\b'.format(string.lower()), string2.lower()) != None:
            number_of_matches += 1
    return number_of_matches
    
def prepare_emojicons(query, responses_dict):
    emojicons = []
    i = 0
    while i < 10:
        emojicon = find_best_emoji(query, responses_dict, emojicons)
        if emojicon is not None:
            emojicons.append(emojicon)
            i += 1
            
        else:
            i = 10
            break
    
    return emojicons
    
def find_best_emoji(query, response_dict, emojicons):
    
    last_matched = 0
    best_match = -1
    flag = False
    for num, each in enumerate(response_dict["Emojicons"]):
        matched = matched_strings(query, each["Nome"])
        if matched > last_matched:
            for resp in emojicons:
                if each == resp:
                    flag = True
                    break
            if flag:
                flag = False
                continue
            best_match = num
            last_matched = matched
    if best_match == -1:
        return {}
    else:

        return response_dict["Emojicons"][best_match]
        

def newemojicon(name, emojicon, response_dict):
    emojidict = {}
    emojidict["Nome"] = name
    emojidict["Emojicon"] = emojicon
    response_dict["Emojicons"].append(emojidict)
    json.dump(response_dict, open("emojicons.json", 'w'), indent=3)