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

mainTypeName = ''
if len(sys.argv) > 3:
    mainTypeName = sys.argv[3]

objs = []
for i, o in enumerate(u):
    objs.append(o)

if DEBUG:
    print(objs)
    for i, o in enumerate(objs):
        with open(f'obj_{i}.json', 'w') as f:
            json.dump(o, f, ensure_ascii=False, indent=4)

assert len(objs) == 3
assert objs[0] == '1'
mappingDef = objs[1]
rawData = objs[2]

CLASS_REGEX = r'''(?m)\[X3MessagePackObject\((.*?)\)\]
.*?(?:class|enum) (%s)(?:| : (.*?))\s// TypeDefIndex.*?\s{(?:
	// Fields
([\S\s]*?))*(?:
	// Properties
([\S\s]*?))*
	// Methods
'''

dumpCsContent = open(r'D:\Workspaces\IDAWorkspace\evol_deepspace\android_rev\good_il2cpp_dump\dump.cs', encoding='utf-8').read()

def findX3MsgPackClass(className):
    print('finding x3msgpack ', className)
    m = next(re.finditer(CLASS_REGEX % re.escape(className), dumpCsContent))
    customName, className, baseClasses, fieldsBody, propsBody = m.groups()
    # print(customName, className, fieldsBody, propsBody)
    
    props = []
    if fieldsBody:
        props += re.findall(r'(?m)^\s*public (.*?) ([A-Za-z0-9_-]+);', fieldsBody)
    if propsBody:
        props += re.findall(r'(?m)^	public (.*?) ([^\s]+?) \{ get; set; \}$', propsBody)
    actualName = className if customName == 'null' else customName.strip('"')
    
    # generate propName -> propType map
    propMap = {
        name: typ for typ, name in props
    }
    
    return actualName, baseClasses, propMap

def findFullX3MsgPackClass(className):
    retMap = {}
    actualName, baseClasses, curPropMap = findX3MsgPackClass(className)
    if baseClasses:
        assert '<' not in baseClasses and '>' not in baseClasses, 'unsupported base class: %s' % (baseClasses)
        baseClasses = baseClasses.strip().split(',')
        for baseClass in baseClasses:
            _, propMap = findFullX3MsgPackClass(baseClass)
            retMap.update(propMap)
    retMap.update(curPropMap)
    return actualName, retMap

# print(findX3MsgPackClass('ActorCfgs'))

class X3MappedType():
    def __init__(self, typName, className, props, mapping) -> None:
        self.typName = typName
        self.className = className
        self.props = props
        self.mapping = mapping
        
mappingTypes = {}
for typName, typMapping in mappingDef.items():
    if not mainTypeName:
        mainTypeName = typName
    clsName, props = findFullX3MsgPackClass(typName)
    mappingTypes[typName] = X3MappedType(typName, clsName, props, typMapping)
print('all types:', mappingTypes)

def parseData(curType, curData):
    if curData is None:
        return None
    if curType in ['string', 'int', 'bool', 'float']:
        return curData
    if curType in ("Vector2", "Vector3", "S2Int", "S2StrInt", "S3Int", "X3Vector3"):
        return [curType, *curData]
    print('parsing ', curType)
    if curType not in mappingTypes and type(curData) not in [dict, list]:
        # probably enum type
        return curData
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
    
    t = mappingTypes[curType] # type: X3MappedType
    ret = {}
    for propName, idx in t.mapping.items():
        if propName.endswith('k__BackingField'):
            continue # ignore compiler generated backing fields
        data = curData[idx]
        
        if not propName in t.props:
            parsed = data
        else:
            propType = t.props[propName]
            parsed = parseData(propType, data)
        ret[propName] = parsed
    ret['_x3tb_type'] = curType
    return ret

data = parseData(mainTypeName, rawData)
import os
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(json.dumps(data, indent=2))