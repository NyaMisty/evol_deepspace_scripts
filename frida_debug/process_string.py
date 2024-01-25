import re
buf = open('stringhashs.txt').read()
s = re.findall(r'CommonUtility__StringToHash: (.*?)\n', buf)

s = list(set(s))
s.sort()

import json
with open('strings.json', 'w') as f:
    f.write(json.dumps(s, indent=4))
