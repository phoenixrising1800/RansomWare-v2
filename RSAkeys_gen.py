"""Generate RSA Encryption/Decryption Public/Private keys on instigator machine """
from Cryptodome.PublicKey import RSA

key = RSA.generate(2048)

priv_key = key.export_key()
with open('privkey.pem', 'wb') as f:
    f.write(priv_key)

pub_key = key.publickey().export_key()
with open('pubkey.pem', 'wb') as f:
    f.write(pub_key)