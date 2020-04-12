#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import json

import requests
import sys

print('* starting\n')

def check(should_code, desc, is_code, return_data, url, cond):
    print('*  tested ' + url + ' using ' + cond + ' (' + desc + ')')

    if(should_code == is_code):
        print('*    ✔ (' + str(is_code) + ')')
    else:
        print('*    ✗ (' + str(is_code) + ')')

    if(option['print_json']):
        print(json.dumps(return_data, sort_keys=True, indent=4, separators=(',', ': ')))

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
                conds.append('no-body')

            if('headers' in p[key][location]['methods'][method]):
                headers = p[key][location]['methods'][method]['headers']

                for header in headers:
                    if(headers[header].startswith('{from}')):
                        opts = headers[header].replace('{from}', '').split(':')
                        headers[header] = storage[opts[0]]['default'][opts[1]]

                conds.append('no-headers')

            storage[location] = {}

            for cond in conds:
                if(cond == 'default'):
                    res = requests.request(method.upper(), url, data=body, headers=headers)
                    check(p[key][location]['methods'][method]['should'][cond], p[key][location]['methods'][method]['description'], res.status_code, res.json(), url, cond)
                    storage[location][cond] = res.json()
                if(cond == 'no-params'):
                    pass
                if(cond == 'no-body'):
                    res = requests.request(method.upper(), url, data={}, headers=headers)
                    check(p[key][location]['methods'][method]['should'][cond], p[key][location]['methods'][method]['description'], res.status_code, res.json(), url, cond)
                    storage[location][cond] = res.json()
                if(cond == 'no-headers'):
                    res = requests.request(method.upper(), url, data=body, headers={})
                    check(p[key][location]['methods'][method]['should'][cond], p[key][location]['methods'][method]['description'], res.status_code, res.json(), url, cond)
                    storage[location][cond] = res.json()

            print()
