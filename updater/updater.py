#!/usr/bin/env python
# coding: utf-8

import json
import requests
import hashlib
import time
import sys

if len(sys.argv) < 3:
    print("usage: python3 updater.py [cdnver] [platform]\nyou can use 'latest' to auto specify latest cdn version")
    sys.exit(1)

cdnver = sys.argv[1]
platform = sys.argv[2]

sess = requests.Session()
def doReq(meth, url, *args, **kwargs):
    params = {}
    if 'params' in kwargs:
        params = kwargs.pop('params')
        params = dict(params)
    params['timestamp'] = str(int(time.time()))
    params['clientid'] = "1068"
    clientKey = 'JWTY912Pdrmd'
    params['sig'] = hashlib.md5((clientKey + params['timestamp']).encode()).hexdigest()
    kwargs['params'] = params
    return sess.request(meth, url, *args, **kwargs)


r = doReq('GET', 'https://api-deepspace.papegames.com:12101/v1/gameconfig/patchlist?channel=1&role=0&build=70&apkversion=1.0.1&region=1')
patch_config = r.json()['game_config_patch']
patch_config

cdnurl = patch_config['extra']['cdn_url'].split(';')[0]
if cdnver == 'latest':
    cdnver = patch_config['extra']['hotfix_version'].split(';')[0]
#https://x3cn-client.papegames.com/prd/1.0.2536/respatch_ios/patch_res/res_patch_catalog.bin?
patch_base_url = f'{cdnurl}/{cdnver}/respatch_{platform}/patch_res'
patch_base_url


respatch_catalog = sess.get(patch_base_url + '/res_patch_catalog.bin?').content

assert respatch_catalog[:8] == b'-!patch!'

import io
import struct
class DataTransfer():
    def __init__(self, f):
        self.f = f
    
    def read(self, n):
        ret = self.f.read(n)
        if len(ret) != n:
            raise Exception("short read")
        return ret
    
    def readUInt16(self):
        return int.from_bytes(self.read(2), 'little')
    def readUInt32(self):
        return int.from_bytes(self.read(4), 'little')
    def readFloat(self):
        return struct.unpack("f", self.read(4))[0]
    def readString(self):
        return self.read(self.readUInt16()).decode()
    def readList(self, readFunc):
        listLen = self.readUInt32()
        ret = []
        for i in range(listLen):
            ret.append(readFunc(self))
        return ret
    def readUInt32List(self):
        return self.readList(lambda t: t.readUInt32())
            
t = DataTransfer(io.BytesIO(respatch_catalog[40:]))
def readResPatchCatalog(t):
    ret = {}
    ret['VersionString'] = t.readString()
    ret['VersionNum'] = t.readUInt32()
    ret['PackageCountPercentThreshold'] = t.readFloat()
    ret['SmallPackageCountPercentThreshold'] = t.readFloat()
    def readResInfo(t):
        ret = {}
        ret['m_filePath'] = t.readString()
        ret['m_size'] = t.readUInt32()
        ret['m_hash'] = t.readUInt32()
        return ret
    ret['ResInfoList'] = t.readList(readResInfo)
    def readResPkgInfo(t):
        ret = {}
        ret['TagIndex'] = t.readUInt32()
        ret['m_filePath'] = t.readString()
        ret['m_size'] = t.readUInt32()
        ret['m_rawSize'] = t.readUInt32()
        ret['m_hash'] = t.readUInt32()
        ret['ResInfoIndexList'] = t.readUInt32List()
        def readResPackageVolumeInfo(t):
            ret = {}
            ret['m_filePath'] = t.readString()
            ret['m_size'] = t.readUInt32()
            ret['m_rawSize'] = t.readUInt32()
            ret['m_hash'] = t.readUInt32()
            return ret
        ret['ResPkgVolumeInfoList'] = t.readList(readResPackageVolumeInfo)
        return ret
    ret['ResPkgInfoList'] = t.readList(readResPkgInfo)
    # TODO: fix CustomUserData
    t.readUInt32()
    ret['CustomUserData'] = []
    def readModifiedNotificationResInfo(t):
        ret = {}
        ret['ResIndex'] = t.readUInt32()
        ret['UserData'] = t.readString()
        return ret
    ret['ModifiedNotificationResInfos'] = t.readList(readModifiedNotificationResInfo)
    return ret

catalog = readResPatchCatalog(t)
catalog

with open(f'catalogs/{cdnver}.json', 'w') as f:
    json.dump(catalog, f, indent=4, ensure_ascii=False)

# 保证所有res pkg加起来能完整覆盖全部的resinfo
indexs = list(set(sum((c['ResInfoIndexList'] for c in catalog['ResPkgInfoList']), [])))
assert indexs[-1] == len(indexs) - 1

# for single resource: https://x3cn-client.papegames.com/prd/1.0.2536/respatch_ios/patch_res/Total/XFileZip/968647023.zip
# for a package: https://x3cn-client.papegames.com/prd/1.0.2536/respatch_ios/patch_res/Packages/c-35.zip
allfiles = [f'{patch_base_url}/{c["m_filePath"]}' for c in catalog['ResPkgInfoList']]
with open('/tmp/update_packages.txt', 'w') as f:
    f.write(json.dumps(allfiles))
