# %%
import binascii
binascii.crc32(b'5e/39/4e372614206d06dc36e94726544d.ab')

# %%
def Utils__CalculateStringCrcHashString(buf, acquiredLength):
    _crc = binascii.crc32(buf.encode())
    ret = ""
    crc = _crc
    for i in range(acquiredLength):
        if i % 2 == 0:
            ret += chr(b'a'[0] + (crc % 10))
        else:
            ret += chr(b'0'[0] + (crc % 10))
        if crc < 10:
            crc = _crc
        else:
            crc = int(crc/10)
    return ret

assert 'i7h0i3e3b2i7h0i3' == Utils__CalculateStringCrcHashString('5e/39/4e372614206d06dc36e94726544d.ab', 16)

# %%
def DeriveKey(codeBook):
    ret = b''
    codeBook = codeBook.encode()
    DERIVE_CONST = [0x05, 0x6B, 0x35]
    ret += bytes([c ^ DERIVE_CONST[2] for c in codeBook])
    ret += bytes([c ^ DERIVE_CONST[1] for c in codeBook])
    ret += bytes([c ^ DERIVE_CONST[0] for c in codeBook])
    ret += codeBook
    return ret

k = DeriveKey(Utils__CalculateStringCrcHashString('95/14/fff9bd18d2edeb16aa4f62d9bc9a.ab', 16))
#print(k.hex())
t = bytes.fromhex('08 6A 3E 78 26 46 01 0D 50 06 5D 03 62 22 27 2E')
d = bytes([t[i] ^ k[i % len(k)] for i in range(len(t))])
assert d.startswith(b'UnityFS')

# %%
from Crypto.Util import strxor
def DecryptBundle(bundleBasePath, bundlePath):
    # bundle path like: XX/XX/XXXXXXXXXXXXXXXXXX.ab
    with open(f'{bundleBasePath}/{bundlePath}', 'rb') as f:
        t = f.read()
    k = DeriveKey(Utils__CalculateStringCrcHashString(bundlePath, 16))
    if False:
        #d = bytes([t[i] ^ k[i % len(k)] for i in range(len(t))])
        d = bytes(t[i] ^ k[i % len(k)] for i in range(len(t)))
        #d = bytes((k[i % len(k)] for i in range(len(t))))
    else:
        kk = k * (len(t) // len(k) + 1)
        kk = kk[:len(t)]
        assert len(t) == len(kk)
        d = strxor.strxor(t, kk)
        #assert d == bytes([t[i] ^ k[i % len(k)] for i in range(len(t))])
    assert d.startswith(b'Unity'), f'invalid header: {d[:16].hex()}'
    return d

import os
import sys
if False:
    BUNDLE_BASE = '/mnt/d/Workspaces/IDAWorkspace/evol_deepspace/lysk/assets/bundles'
    BUNDLE_DEC = '/mnt/d/Workspaces/IDAWorkspace/evol_deepspace/lysk/assets/bundles_dec'
else:
    BUNDLE_BASE = sys.argv[1]
    BUNDLE_DEC = sys.argv[2]
import zipfile

outzip = BUNDLE_DEC.endswith('.zip')
if outzip:
    zipF = zipfile.ZipFile(BUNDLE_DEC, 'w')

def fileIter():
    for root, dirs, files in os.walk(BUNDLE_BASE):
        for f in files:
            if f.startswith('abconfig'):
                continue
            bundle = os.path.relpath(root, BUNDLE_BASE) + '/' + f
            outputFullPath = BUNDLE_DEC + '/' + bundle
            yield bundle, outputFullPath

from multiprocessing.pool import ThreadPool

p = ThreadPool(10)
def dec(task):
    bundle, outputFullPath = task
    print("Decrypting", bundle)
    buf = DecryptBundle(BUNDLE_BASE, bundle)
    return bundle, outputFullPath, buf

for bundle, outputFullPath, d in p.imap_unordered(dec, fileIter()):
    if not outzip:
        os.makedirs(os.path.dirname(outputFullPath), exist_ok=True)
        with open(outputFullPath, 'wb') as f:
            f.write(d)
    else:
        #print(f'Writing {bundle} size {len(d)}')
        zipF.writestr(bundle, d)
if outzip:
    zipF.close()


