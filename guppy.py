#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import json
import time
import requests
import sys

start = time.process_time()
print('* starting\n')

def check(should_code, desc, is_code, return_data, url, cond):
    print('*  tested ' + url + ' using ' + cond + ' (' + desc + ')')

    if(should_code == is_code):
        print('*    ✔ (' + str(is_code) + ')')
    else:
        print('*    ✗ (' + str(is_code) + ')')

    if(option['print_json']):
        print(json.dumps(return_data, sort_keys=True, indent=4, separators=(',', ': ')))

def traverse(body):
    for entry in body:
        if(isinstance(body[entry], str) and body[entry].startswith('{from}')):
            opts = body[entry].replace('{from}', '').split(':')
            pa = opts[1].split(";")
            tmp = storage[opts[0]]['default']
            for i in range(len(pa)):
                tmp = tmp[pa[i]]

            body[entry] = tmp
    return body

CONFIG_NAME = './guppy.yml'
OPTION_NAME = './guppy_options.yml'

try:
    f=open(CONFIG_NAME, 'r')
    p=yaml.load(f)
    if(p):
        print('* config load done')
except:
    print('* error loading config')
    sys.exit(0)

try:
    f=open(OPTION_NAME, 'r')
    option=yaml.load(f)
    if(p):
        print('* options load done')
except:
    option = {'print_json': 0}

print()

storage = {}

for key in p:
    for location in p[key]:
        url = key + "/" + location
        print('* testing ' + url)
        for method in p[key][location]['methods']:
            conds = ['default']
            parameters = {}
            body = {}
            headers = {}

            if('parameters' in p[key][location]['methods'][method]):
                parameters = p[key][location]['methods'][method]['parameters']
                conds.append('no-params')

            if('body' in p[key][location]['methods'][method]):
                body = p[key][location]['methods'][method]['body']
                body = traverse(body)
                conds.append('no-body')

            if('headers' in p[key][location]['methods'][method]):
                headers = p[key][location]['methods'][method]['headers']
                headers = traverse(headers)
                conds.append('no-headers')

            storage[location] = {}

            for cond in conds:
                if(cond == 'default'):
                    res = requests.request(method.upper(), url, data=body, headers=headers)
                if(cond == 'no-params'):
                    pass
                if(cond == 'no-body'):
                    res = requests.request(method.upper(), url, data={}, headers=headers)
                if(cond == 'no-headers'):
                    res = requests.request(method.upper(), url, data=body, headers={})

                try:
                    js = res.json()
                    storage[location][cond] = res.json()
                except:
                    print('*    - unable to decode json')
                    js = res.text
                    storage[location][cond] = {}

                if('should' in p[key][location]['methods'][method] and cond in p[key][location]['methods'][method]['should']):
                    should_cond = p[key][location]['methods'][method]['should'][cond]
                else:
                    # setting default parameters
                    print('*  - no default parameter defined for ' + cond + '. using: ', end='')
                    if(cond == 'no-body'):
                        should_cond = 400
                    elif(cond == 'no-headers'):
                        should_cond = 401
                    elif(cond == 'no-params'):
                        shoud_cond = 404
                    print(should_cond)

                if('description' in p[key][location]['methods'][method]):
                    desc = p[key][location]['methods'][method]['description']
                else:
                    desc = ''

                check(should_cond, desc, res.status_code, js, url, cond)


            print()
print('* done testing in ' + str( round((time.process_time() - start), 2) ) + 's')
