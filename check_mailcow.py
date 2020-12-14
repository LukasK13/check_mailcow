#!/usr/bin/python3

import requests as req
import argparse
import sys

parser = argparse.ArgumentParser(prog="check_mailcow.py", description='Check Mailcow API')
parser.add_argument("-d", "--domain", dest='domain', default="localhost",
                    metavar="mailcow.local", help="Domain name and optional port number for the Mailcow API.")
parser.add_argument("-e", "--endpoint", dest="endpoint", default="status/containers",
                    metavar="API-Endpoint", help="API endpoint to check with the Mailcow API.")
parser.add_argument("-s", "--ssl", dest="ssl", default=False, action='store_true', help="Use SSL for the connection.")
parser.add_argument("-i", "--insecure", dest="verify", default=True, action='store_false',
                    help="Insecure connection. Don't verify the SSL certificate.")
parser.add_argument("-k", "--key", dest="key", metavar="API-key", help="Key for the Mailcow API.", required=True)

parser.add_argument("-w", "--warning", dest="warning", metavar="Warning Treshold", default=75,
                    help="Value above which the result is considered warning")
parser.add_argument("-c", "--critical", dest="critical", metavar="Critical Treshold", default=90,
                    help="Value above which the result is considered critical")
args = parser.parse_args()

headers = {"Content-Type": "application/json", "X-API-Key": args.key}
try:
    res = req.get(("https" if args.ssl else "http") + "://" + args.domain + "/api/v1/get/" + args.endpoint,
                  headers=headers, verify=args.verify)
except:
    print("Unknown: Connection to {host} refused.".format(host=args.domain))
    sys.exit(3)

if res.status_code == 200:
    try:
        nodes = res.json()

        if args.endpoint == "status/containers":
            """ Returns a dictionary with each container being the key for its information"""
            container_state = [nodes[i]['state'] == "running" for i in nodes.keys()]
            if all(container_state):
                print("OK: All containers in state 'running'. | containers_up={containers}".format(containers = len(nodes)))
            else:
                running_containers = [nodes[i]['container'] for i in nodes.keys() if nodes[i]['state'] == "running"]
                failed_containers = [nodes[i]['container'] for i in nodes.keys() if nodes[i]['state'] != "running"]
                failed_container_list = ", ".join(failed_containers)
                print(
                    "Critical: Containers {containers} are not running. | containers_up={num_up} containers_down={num_down} "
                    .format(
                        num_up = running_containers,
                        num_down = failed_container_list
                    )
                )
                sys.exit(2)
        elif args.endpoint == "status/solr":
            if nodes['solr_enabled']:
                print("OK: Solr up and running. | documents={documents} size={size}".format(documents = nodes['solr_documents'], size = nodes['solr_size'].replace(" ", "")))
            else:
                print("Warning: Solr is not running.")
                sys.exit(1)
        elif args.endpoint == "status/vmail":
            percent_used = int(nodes['used_percent'].replace("%", ""))
            if percent_used < int(args.warning):
                print(
                    "OK: vmail has sufficient storage. | vmail_used_percent={used_percent};{warn};{crit} vmail_used_size={used_size}"
                    .format(
                        used_percent = nodes['used_percent'],
                        used_size = nodes['used'].replace("G", "GB"),
                        warn = args.warning,
                        crit = args.critical
                    )
                )
            elif int(args.warning) <= percent_used < int(args.critical):
                print(
                    "Warning: vmail is short on storage. | vmail_used_percent={used_percent};{warn};{crit} vmail_used_size={used_size}"
                    .format(
                        used_percent = nodes['used_percent'],
                        used_size = nodes['used'].replace("G", "GB"),
                        warn = args.warning,
                        crit = args.critical
                    )
                )
                sys.exit(1)
            else:
                print(
                    "Critical: vmail is critically low. | vmail_used_percent={used_percent};{warn};{crit} vmail_used_size={used_size}"
                    .format(
                        used_percent = nodes['used_percent'],
                        used_size = nodes['used'].replace("G", "GB"),
                        warn = args.warning,
                        crit = args.critical
                    )
                )
                sys.exit(2)
        else:
          print("Unknown endpoint {endpoint} supplied".format(endpoint = args.endpoint))
          sys.exit(3)
    except ValueError:
        print("Unknown: No json returned from endpoint. Response was {response}".format(response = res.text if len(res.text) > 0 else "empty"))
        sys.exit(3)
else:
    print("Unknown: Request returned status code " + str(res.status_code) + ".")
    sys.exit(3)
