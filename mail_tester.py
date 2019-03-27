import dns.resolver
import telnetlib
import time
from stem import Signal
from stem.control import Controller
import socks
import argparse
import re
import csv


controller = Controller.from_port(port = 9051)

def get_tor_session():
	"""
	Init tor first session
	"""
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"localhost",9050) 
	socks.wrapmodule(telnetlib)

def reset_tor_session(mot_de_passe):
	"""
	Reset tor session (may take some times)
	"""
	controller.authenticate(password=mot_de_passe)
	controller.signal(Signal.NEWNYM)

def mx_server_find(domain):
	"""
	Allow to find mx server attach to a domain name
	"""
	preference = 10000
	table_answers = []
	answers = dns.resolver.query(domain, 'MX')
	for contenu in answers:
		table_answers.append([contenu.exchange,contenu.preference])
		if contenu.preference < preference:
			preference = contenu.preference
			mx_server = str(contenu.exchange)
	mx_server = mx_server[:-1]
	return mx_server

def telnet_connection(mx_host,mail):
	"""
	Launch telnet connection through TOR
	"""
	tn = telnetlib.Telnet()
	tn.set_debuglevel(100)
	tn.open(host=mx_host,port=25)
	tn.expect([b"220.*"],timeout=20)
	tn.write(b"HELO toto\n")
	tn.expect([b"250.*"],timeout=20)
	tn.write(b"mail from: <toto@toto.fr>\n")
	tn.expect([b"250.*"],timeout=10)
	tn.write(b"rcpt to: <"+mail+b">\n")
	result = tn.expect([b"250.*"],timeout=3)
	tn.close()
	return result[0]


def telnet_connection_multiple_mail(mx_host,list_mail,password):
	"""
	Launch telnet connection through TOR for multiple mail
	"""
	output = []
	i = 0
	tn = telnetlib.Telnet()
	# tn.set_debuglevel(100)
	tn.open(host=mx_host,port=25)
	tn.expect([b"220.*"],timeout=20)
	tn.write(b"HELO toto\n")
	tn.expect([b"250.*"],timeout=20)
	tn.write(b"mail from: <toto@toto.fr>\n")
	tn.expect([b"250.*"],timeout=10)
	for element in list_mail:
		if i == 30:
			reset_tor_session(password)
			i = 0
			time.sleep(15)
		else:
			i = i + 1
			tn.write(b"rcpt to: <"+element.encode()+b">\n")
			result = tn.expect([b"250.*"],timeout=3)
			if result[0] == 0:
				output.append([element,True])
			else:
				output.append([element,False])
	tn.close()
	return output

def get_args():
	"""
	Get args from the cli
	"""
	parser = argparse.ArgumentParser(description='Mailtester over TOR written in python3.7')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-f', '--file', action='store', help="list of mail in file")
	group.add_argument('-m', '--mail', action='store')
	parser.add_argument('-p', '--password', type=str, default="test", help="Put your TOR password Controller")
	parser.add_argument('-o', '--output', type=str, default="listingmail.csv", help="Only for -f option, allow to output data into a file")
	args = parser.parse_args()
	if args.mail is None:
		return args.file,args.password,0,args.output
	else:
		if re.search(r'[\w.-]+@[\w.-]',args.mail):
			return args.mail,args.password,1,args.output
		else:
			raise ValueError("Not a mail address")

def get_domain_mail(mail):
	"""
	Allow to get domain name associate to a single mail address
	"""
	regex = re.match(r'.*@(.*)',mail)
	if regex is not None:
		return regex.group(1)
	else:
		raise ValueError("No domain found")

def get_domain_file(file):
	"""
	Allow to get domain name associate to a list of mail address
	"""
	file_content = []
	domain_list = []
	with open(file) as f:
		file_content = f.read().splitlines()
	for contenu in file_content:
		regex = re.match(r'.*@(.*)',contenu)
		if regex is not None:
			if regex.group(1) not in domain_list:
				domain_list.append(regex.group(1))
	# print(len(domain_list),"domain where identify")
	return domain_list,file_content

def mail_list_after_domain(domain,file_content):
	"""
	Separate mail depending on the domain
	"""
	mail_output_listing = []
	for content in contenu_fichier:
		if content.endswith(domain):
			if content not in mail_output_listing:
				mail_output_listing.append(content)
	return mail_output_listing

def csv_output(list_to_csv,filename):
	"""
	Create a CSV file in output
	"""
	with open(filename, 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=";")
		wr.writerows(list_to_csv)


(arg1,arg2,arg3,arg4) = get_args()
get_tor_session()
if arg3 == 1:
	print("Single Mail Input")
	domain = get_domain_mail(arg1)
	mx_server = mx_server_find(domain)
	exist = telnet_connection(mx_server,arg1.encode())
	if exist == -1:
		print("Unknown !")
	else:
		print("Exists !")
elif arg3 == 0:
	list_domain = []
	contenu_fichier = []
	output_traitement = []
	listing_mail_a_traiter = []
	print("File input")
	list_domain,contenu_fichier = get_domain_file(arg1)
	for contenu in list_domain:
		output_traitement_temp = []
		mx_server = mx_server_find(contenu)
		listing_mail_a_traiter = mail_list_after_domain(contenu,contenu_fichier)
		output_traitement_temp = telnet_connection_multiple_mail(mx_server,listing_mail_a_traiter,arg2)
		output_traitement.extend(output_traitement_temp)
	csv_output(output_traitement,arg4)
else:
	raise ValueError("Unknown problem")

