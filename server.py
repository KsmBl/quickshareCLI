#!/usr/bin/python3

from flask import Flask, send_from_directory, abort, request, render_template_string
from flask_cors import CORS
import threading
import string
import random
import time
import os

HOST_OUTSIDE = "0.0.0.0"
PORT_OUTSIDE = 8080

app = Flask(__name__)
CORS(app)

entries = {}
lock = threading.Lock()

def generateRandomPath(length=24):
	pathChars = string.ascii_letters + string.digits
	return ''.join(random.choice(pathChars) for _ in range(length))

def removeEntry(path):
	with lock:
		if path in entries:
			del entries[path]

def scheduleRemoval(path, ttl):
	def task():
		time.sleep(ttl * 60)
		removeEntry(path)
	threading.Thread(target=task, daemon=True).start()

@app.route('/addEntry', methods=['POST'])
def addEntry():
	data = request.json
	path = generateRandomPath()
	entry = {
		'type': data.get('type'), # "file" oder "directory"
		'path': data.get('path'),
		'ttl': data.get('ttl', 20),
		'maxDownloads': data.get('maxDownloads', 1),
		'downloads': 0
	}
	with lock:
		entries[path] = entry
	scheduleRemoval(path, entry['ttl'])
	return {'path': f"http://{HOST_OUTSIDE}:{PORT_OUTSIDE}/{path}"}

@app.route('/<path:path>', methods=['GET'])
def handlePath(path):
	with lock:
		entry = entries.get(path)
		if not entry:
			return abort(404)

		if entry['downloads'] >= entry['maxDownloads'] and entry['type'] == 'file':
			removeEntry(path)
			return abort(403)

		if entry['type'] == 'file':
			entry['downloads'] += 1
			dirname, filename = os.path.split(entry['path'])
			return send_from_directory(dirname, filename, as_attachment=True)

		elif entry['type'] == 'directory':
			files = os.listdir(entry['path'])
			htmlTemplate = '<h1>Dateien im Verzeichnis</h1><ul>'
			for f in files:
				filePath = f"{path}/{f}"
				htmlTemplate += f'<li><a href="/{path}/{f}">{f}</a></li>'
			htmlTemplate += '</ul>'
			return render_template_string(htmlTemplate)

		elif entry['type'] == 'directoryFile':
			parentPath = entry['parent']
			entry['downloads'] += 1
			return send_from_directory(parentPath, entry['filename'], as_attachment=True)

		else:
			return abort(404)

@app.route('/<path:dirPath>/<path:fileName>', methods=['GET'])
def handleDirFile(dirPath, fileName):
	with lock:
		dirEntry = entries.get(dirPath)
		if not dirEntry or dirEntry['type'] != 'directory':
			return abort(404)

		fullPath = os.path.join(dirEntry['path'], fileName)
		if not os.path.isfile(fullPath):
			return abort(404)

		# Download-Limit für Verzeichnisdateien: jede Datei zählt separat
		dirEntry['downloads'] += 1
		if dirEntry['downloads'] > dirEntry['maxDownloads']:
			removeEntry(dirPath)

		return send_from_directory(dirEntry['path'], fileName, as_attachment=True)


@app.route('/listRoots', methods=['GET'])
def listRoots():
	rootsBase = "/srv"
	allDirs = []
	try:
		for disk in os.listdir(rootsBase):
			diskPath = os.path.join(rootsBase, disk)
			if os.path.isdir(diskPath):
				for sub in os.listdir(diskPath):
					subPath = os.path.join(diskPath, sub)
					if os.path.isdir(subPath):
						relPath = os.path.relpath(subPath, rootsBase)
						allDirs.append(relPath)
		return {"roots": allDirs}
	except Exception as e:
		return {"error": str(e)}, 500


if __name__ == '__main__':
	app.run(host=HOST_OUTSIDE, port=PORT_OUTSIDE, threaded=True)
