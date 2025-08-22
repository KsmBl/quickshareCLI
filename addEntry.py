#!/usr/bin/python3

import argparse
import requests
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--ttl', type=int, default=20, help='Abklingzeit in Minuten')
	parser.add_argument('-a', '--amount', type=int, default=1, help='Maximale Downloads')
	parser.add_argument('-f', '--file', type=str, help='Pfad zur Datei')
	parser.add_argument('-d', '--directory', type=str, help='Pfad zum Verzeichnis')
	args = parser.parse_args()

	if args.file and args.directory:
		print('Error: -f and -d does not work at the same time.')
		return

	if not args.file and not args.directory:
		args.directory = './'

	data = {
		'ttl': args.ttl,
		'maxDownloads': args.amount
	}

	if args.file:
		if not os.path.isfile(args.file):
			print('Fehler: Datei existiert nicht.')
			return
		data['type'] = 'file'
		data['path'] = os.path.abspath(args.file)
	elif args.directory:
		if not os.path.isdir(args.directory):
			print('Fehler: Verzeichnis existiert nicht.')
			return
		data['type'] = 'directory'
		data['path'] = os.path.abspath(args.directory)

	response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/addEntry", json=data)
	if response.status_code == 200:
		print('Path:', response.json()['path'])
	else:
		print('Error:', response.text)

if __name__ == '__main__':
	main()
