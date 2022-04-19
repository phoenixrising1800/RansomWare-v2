""" When executed, decrypts encrypted system files 

Uses hardcoded private key to decrypt all files
1. Traverse system
2. For each file, decrypt the embedded/encrypted AES session key
3. Decrypt the file with the decrypted AES session key
"""
PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAkhgXKdG6b2S3AjafAdmc0g0+saoV+Vn/nh0oDceLTiX7qenM
wJGAvCSaGZTDXv+nbfSIs6nLVd4jkgdpUyL2u2gpVPRMXP/NEJSaPDUq0s1uvpBl
5ujgjWCnfXOcSjzaizL/tqBqRm9jrBDdnogFZ40xKMePxWvukP3XzREFDaoBlYlz
jv7rg4jz9NzRNlCoC5GWajkp7/Q4cums82nqzBQoT1vI6+5UlSU+GDVertMNRCTb
+HabkPVLAGvG4qncBoHlnxuDQ2Grl6+3njOrsw+uykWsefFxO1VIaVnDQIMZQ+JM
CiCErdzTpzwNj6HUG7ER8bp7MCLgRoGhuooPMQIDAQABAoIBABHGiJr3/70p/fJw
/uvUtHYCUox/a2kJgEaWuZbjnpmFmZdU8SrFCWra8T0HkrXuWUrRpAhoMmtiOeW8
rR4GdQrcY5sIlnoCTcskqZeFyI4ZnM3m998emqPZDMgA1xVZTiX9sIth/UxQpUn8
S1rMpguxbDfQADg/J6nQmP9EgN7mj2mlj4lBl1c6ZYF3jyJA0i8P2yjlJ0jR1SLY
yRIKXJTMp9Mypr6DgVvKNSJ1eeZCPcbxbucyismRrAvBeJvWmZBw9GIiIbnrH/Gg
IkOGG/02RD2H/kuty5p/vcWhURALWzL33i0b61+L6aG1LW+NRzw65mGkFNzx1The
JUTS/VkCgYEAuHTnjemdMx6UZruuNb3VMicRb3t2782buopH3WsrKpy8bZkgX/pk
K4zu+hITSoa2op+ZJuv/ZHsdCuI5eSo4+rxHJDYH0noyWtD/wR2/3Jgxqrctnu3w
Gs5gCoY8qDX6o+nho5x4b2Aiyx5HMGD93YA0Ej4itkW4SF/AbipMgGcCgYEAysIW
AzhRtpH5V/+uXQBp2nJ29o80xQS1qPiO75wrBMlnYE+MDtJDFds3Mvy9MgWwzTqw
45Rpy8n/4Svz4Y0Pr/G7uWnlJM8xcFe7dbXMPW/vf43q63ZtndDzsSlzko3TiupP
Nm00PDsxfOSvSg6DYl2FxppHnt8HcyrmhLEr1KcCgYEAqy16Ud1x0CXZzHjxk9gG
iNNuv8mRN7vUgEmhpZ614Yaw6vjG7ar92NiiUhoCIxBfXw3DYDZ0vTfvXNFSStpf
JHkjgDxQCAj0wAjiv8Gu8rWeqfHyeWIQh5/ryviGRAhMAF+k0WP89EcAIwWHRSNN
lIhMSn21Uvfiq++IMfQ5KJMCgYEAyj9nbbbT62UYbyrfZm1vKTNcbvzSCmR0QCQP
j/sa/h9YOr2eW3po6HhOS1HH9wmuHkkZASmdjmXkE1ugXbAzobFjK8PxihISopkg
qH27SN1K7NVHK7BqDy3Kp0FNwzYteTfX49ZycFIrPwVtxFVNwOTA+CYUouidqcd1
QY7oxakCgYA7rujAmkQeVCk7C6uVEO9bmte2TZYXvi4ewnpq8GM1l3EuxUF90JKr
vuHRBDIbobcDP5S9dct3s27AXFq40dqrFttsajYBt+GUg2CSIt1V/9FFBO8VvT8o
yLGl4KIi4pJPMAhyuqz1mdk40BmaNOqQ8xxI6C8v+cv8U6MN8Kfn5A==
-----END RSA PRIVATE KEY-----'''
import os
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP

def main():
    print("Decrypting system...")
    priv = RSA.import_key(PRIVATE_KEY.encode())

    #1. Traverse system
    #traverse_path = os.cwd()
    traverse_path = os.path.expanduser('~')
    sys_files = os.walk(traverse_path) 
    for root, dir, files in sys_files:
        for file in files:
            if '.encrypted' in file:
                print(file + ' --> ' + file.split('.encrypted')[0])
                path = root + '\\' + file

                # read enc
                with open(path, 'rb') as f:
                    enc_aes, nonce, tag, ciphertext = \
                        [ f.read(x) for x in (priv.size_in_bytes(), 16, 16, -1) ]

                # dec aes with priv
                c_rsa = PKCS1_OAEP.new(priv)
                aes = c_rsa.decrypt(enc_aes)

                # dec data w aes
                c_aes = AES.new(aes, AES.MODE_EAX, nonce)
                data = c_aes.decrypt_and_verify(ciphertext, tag)

                #write pltxt into new
                oldf = root + '\\' + file.split('.encrypted')[0]  
                with open(oldf, 'wb') as f:
                    f.write(data)

                os.remove(path)

if __name__ == '__main__':
    main()