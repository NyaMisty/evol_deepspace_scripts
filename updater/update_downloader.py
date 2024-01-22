#!/usr/bin/env python
# coding: utf-8

import json
import requests
import hashlib
import time
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    
def subcall(*args, **kwargs):
    eprint("Calling %s" % args)
    subprocess.check_call(*args, **kwargs)


with open('catalogs/latest.json') as f:
    catalog = json.load(f)

patch_base_url = catalog['patch_base_url']
urls = []
for pkgInfo in catalog['ResPkgInfoList']:
    if pkgInfo["m_filePath"]:
        # non-split
        urls.append(f'{patch_base_url}/{pkgInfo["m_filePath"]}')
    elif pkgInfo["ResPkgVolumeInfoList"]:
        for subvolume in pkgInfo["ResPkgVolumeInfoList"]:
            urls.append(f'{patch_base_url}/{subvolume["m_filePath"]}')


import subprocess
for i, fileurl in enumerate(urls):
    subcall(['aria2c', '-x', '16', '-s', '16', fileurl, '-d', '/tmp', '-o', f'evol_{i}.zip'])
    subcall(['unzip', '-d', f'.', '-o', f'/tmp/evol_{i}.zip'])
    subcall(['rm', '-f', f'/tmp/evol_{i}.zip'])
