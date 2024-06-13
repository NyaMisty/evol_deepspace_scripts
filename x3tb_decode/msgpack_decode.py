from calendar import c
from email.utils import parsedate
import sys
import json
import re
from msgpack import Unpacker

DEBUG = False

u = Unpacker(strict_map_key=False)

INPUT_FILE = sys.argv[1]
with open(sys.argv[1], 'rb') as f:
    u.feed(f.read())

if len(sys.argv) > 2 and sys.argv[2]:
    OUTPUT_FILE = sys.argv[2]
else:
    OUTPUT_FILE = INPUT_FILE + "_dec.json"

mainTypeName = sys.argv[3]

objs = []
for i, o in enumerate(u):
    objs.append(o)

if DEBUG:
    # print(objs)
    for i, o in enumerate(objs):
        with open(f'obj_{i}.json', 'w') as f:
            json.dump(o, f, ensure_ascii=False, indent=4)

assert len(objs) == 1
rawData = objs[0]

# CLASS_REGEX = r'''(?m)\[MessagePackObject\(.*?\)\](?:\n\[.*?\])*
# .*?(?:class|enum) (%s)(?:| : (.*?))\s// TypeDefIndex.*?\s{(?:
# 	// Fields
# ([\S\s]*?))*(?:
# 	// Properties
# ([\S\s]*?))*
# 	// Methods
# '''
CLASS_REGEX = r'''(?m)(?:class|enum) (%s)(?:| : (.*?))\s// TypeDefIndex.*?\s{(?:
	// Fields
([\S\s]*?))*(?:
	// Properties
([\S\s]*?))*
	// Methods
'''

dumpCsContent = open(r'D:\Workspaces\IDAWorkspace\evol_deepspace\android_rev\good_il2cpp_dump\dump.cs', encoding='utf-8').read()

def findMsgPackClass(className):
    print('finding msgpack ', className)
    m = next(re.finditer(CLASS_REGEX % re.escape(className), dumpCsContent))
    className, baseClasses, fieldsBody, propsBody = m.groups()
    # print(customName, className, fieldsBody, propsBody)
    
    ff = []
    if fieldsBody:
        ff += re.findall(r'(?m)^\s*\[Key\((.*?)\)\]\s*public (.*?) ([A-Za-z0-9_-]+);', fieldsBody)
    if propsBody:
        ff += re.findall(r'(?m)^\s*\[Key\((.*?)\)\]\s*public (.*?) ([^\s]+?) \{ get; set; \}$', propsBody)
    # actualName = className if customName == 'null' else customName.strip('"')
    actualName = className
    
    # generate propName -> propType map
    propMap = {
        int(key): (int(key), name, typ) for key, typ, name in (ff)
    }
    # print(propMap.keys())
    # assert all(c in propMap for c in range(max(propMap.keys())))
    return actualName, baseClasses, propMap

def findFullMsgPackClass(className):
    retMap = {}
    actualName, baseClasses, curPropMap = findMsgPackClass(className)
    if baseClasses:
        assert '<' not in baseClasses and '>' not in baseClasses, 'unsupported base class: %s' % (baseClasses)
        baseClasses = baseClasses.strip().split(',')
        for baseClass in baseClasses:
            _, propMap = findFullMsgPackClass(baseClass)
            retMap.update(propMap)
    retMap.update(curPropMap)
    return actualName, retMap

# print(findMsgPackClass('SkillLevelCfg'))

class X3MappedType():
    def __init__(self, typName, className, mapping) -> None:
        self.typName = typName
        self.className = className
        self.mapping = mapping

_, propTypeMap = findFullMsgPackClass(mainTypeName)
mappingTypes = {}
mappingTypes[mainTypeName] = X3MappedType(mainTypeName, mainTypeName, propTypeMap)

def parseData(curType, curData):
    if curData is None:
        return None
    if curType in ['string', 'int', 'bool', 'float']:
        return curData
    if curType in ("Vector2", "Vector3", "S2Int", "S2StrInt", "S3Int", "X3Vector3"):
        return [curType, *curData]
    if type(curData) not in [dict, list]:
        # probably enum type
        return curData
    print('parsing ', curType)
    # if curType not in mappingTypes and type(curData) not in [dict, list]:
    #     # probably enum type
    #     return curData
    if curType.startswith('Dictionary'):
        m = re.findall(r'^Dictionary<(.*?), (.*?)>$', curType)
        assert m, 'invalid dict type: %s' % curType
        keyType, valueType = m[0]
        ret = {}
        for k, v in curData.items():
            ret[k] = parseData(valueType, v)
        return ret
    if curType.endswith('[]'):
        m = re.findall(r'^(.*?)\[\]$', curType)
        assert m, 'invalid list type: %s' % curType
        valueType = m[0]
        ret = []
        for v in curData:
            ret.append(parseData(valueType, v))
        return ret
    if curType.startswith('List') or curType.startswith('HashSet'):
        m = re.findall(r'^(?:List|HashSet)<(.*?)>$', curType)
        assert m, 'invalid list type: %s' % curType
        valueType = m[0]
        ret = []
        for v in curData:
            ret.append(parseData(valueType, v))
        return ret
    
    if not curType in mappingTypes:
        try:
            _, propTypeMap = findFullMsgPackClass(curType)
            mappingTypes[curType] = X3MappedType(curType, curType, propTypeMap)
        except:
            if type(curData) not in [dict, list]:
                # probably enum type
                return curData
            raise
    t = mappingTypes[curType] # type: X3MappedType
        
    ret = {}
    for propIdx, prop in t.mapping.items():
        _, propName, propType = prop
        # if propName.endswith('k__BackingField'):
        #     continue # ignore compiler generated backing fields
        data = curData[propIdx]
        ret[propName] = parseData(propType, data)
    ret['_x3tb_type'] = curType
    return ret

data = parseData(mainTypeName, rawData)
import os
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(json.dumps(data, indent=2))