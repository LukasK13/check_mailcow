#!/usr/bin/python3

import requests as req
import argparse
import sys

parser = argparse.ArgumentParser(prog="check_mailcow.py", description='Check Mailcow API for container states')
parser.add_argument("-d", "--domain", dest='domain', default="localhost",
                    metavar="mailcow.local", help="Domain name and optional port number for the Mailcow API.")
parser.add_argument("-s", "--ssl", dest="ssl", default=False, action='store_true', help="Use SSL for the connection.")
parser.add_argument("-i", "--insecure", dest="verify", default=True, action='store_false',
                    help="Insecure connection. Don't verify the SSL certificate.")
parser.add_argument("-k", "--key", dest="key", metavar="API-key", help="Key for the Mailcow API.", required=True)
args = parser.parse_args()

headers = {"Content-Type": "application/json", "X-API-Key": args.key}
try:
    res = req.get(("https" if args.ssl else "http") + "://" + args.domain + "/api/v1/get/status/containers",
                  headers=headers, verify=args.verify)
except:
    print("Unknown: Connection refused.")
    sys.exit(3)

if res.status_code == 200:
    containers = res.json()
    container_state = [containers[i]['state'] == "running" for i in containers.keys()]
    if all(container_state):
        print("OK: All containers in state 'running'.")
    else:
        print("Critical: Containers " + ", ".join([containers[i]['container'] for i in containers.keys() if
                                                   containers[i]['state'] != "running"]) + "are not running.")
        sys.exit(2)
else:
    print("Unknown: Request returned status code " + str(res.status_code) + ".")
    sys.exit(3)
