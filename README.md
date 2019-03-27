# Mailtester over TOR

Written in python3.7

## Informations

- Use Tor proxy and Tor Controller

Warnings : 
1. Many SMTP server use technology such as Sophos Spam Filtering that block many (all ?) Tor IP.
2. Before launching the script, verify that you have configured the tor controller (/etc/tor/torrc file) and setup a password (tor --hash-password yourpassword).
3. Start tor service before using the script
- Take single mail or file in input
- If you use file input, output the result into a file
- If you don't want to use Tor proxy, comment the line that are referring to TOR proxy
Warning :
If you do so, the target SMTP server could blacklist your IP

## Installation

pip install -r requirements.txt

## Usage 

python -h
python -m "toto@toto.to"
python -f "file_with_mail.txt" -p "tor_controller_password" -o "ouput_file.csv"



Note 1 : This simple project was done only for my personnal culture, I'm not responsible for any 

Note 2 : This script could be greatly improved so feel free to improve it.
