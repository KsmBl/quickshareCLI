# quickshareCLI:
## usage:
- start server.py
- start addEntry.py with one of the parameters at the next section
- a link will prints to the terminal
- open the link, download the file, the link will get useless after the download

## parameters:
### addEntry.py
- -t | set timeout in minutes. default is 20. When download limit is not exceeded the server will close itself after the given amount of minutes
- -a | set max amount of downloads. default is 1
- -d / -f | specify directory (with -d) or a file (with -f). Only one of them can be used, when nothing is specified "./" will be used
