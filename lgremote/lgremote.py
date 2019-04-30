import json
import os
import asyncio
import websockets
from os.path import abspath, expanduser
import argparse
import re
import subprocess
import sys

import wakeonlan
from netdisco.ssdp import SSDP

from .lgremote_protocol import LGRemoteProtocol

def discover_ip_address():
    """
    Discover WebOS TV's and return ip address
    """
    ssdp = SSDP()
    tvs = ssdp.find_by_device_description({
        "deviceType": "urn:schemas-upnp-org:device:Basic:1",
        "modelName": "LG Smart TV"
    })

    # TODO: handle multiple tvs
    selected_tv = tvs[0]

    return selected_tv.location.split('//')[1].split(':')[0]


def find_mac_address(ip_address):
    """
    Get the mac address associated with an ip address using arp
    """
    response = subprocess.run(["arp", "-n", ip_address],
                              stdout=subprocess.PIPE,
                              universal_newlines=True)
    matches = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", response.stdout)
    
    if not matches:
        return None
    mac = matches.groups()[0]
    m = mac.split(':')
    mac = ':'.join(['%02x' % int(x, 16) for x in m])
    return mac


async def asend(ws_uri, uri, payload, client_key=None):
    """
    Asynchronously send a single request. Returns a tuple (response, 
    client_key), where client_key can be used to make subsequent requests 
    without pairing.
    """
    async with websockets.connect(ws_uri,
            create_protocol=LGRemoteProtocol) as remote:
        client_key = await remote.register(client_key)
        
        await remote.request(uri, payload)
        response = await remote.response()

        return (response, client_key)


def send(ws_uri, uri, request, client_key=None):
    """
    Synchronously send a single request. Returns a tuple (response,
    client_key), where client_key can be used to make subsequent requests 
    without pairing.
    """
    loop = asyncio.get_event_loop()

    (response, key) = loop.run_until_complete(asend(ws_uri, uri, request,
                                                    client_key))

    return (response, key)


def load_settings(settings_file):
    try:
        return json.load(open(settings_file))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        print(error)
        sys.exit(1)


def save_settings(settings_file, settings):
    try:
        json.dump(settings, open(settings_file, 'w'))
    except (OSError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-s', '--settings-file',
            type=lambda fn: abspath(expanduser(fn)), default='~/.lgtv.json')
    parser.add_argument('ssap_uri', metavar='uri-segment', nargs='*', default='')
    parser.add_argument('-p', '--payload', type=json.loads)
    parser.add_argument('--find-mac-address', action='store_true')
    parser.add_argument('--wake', action='store_true')
    
    args = parser.parse_args()

    args.ssap_uri = '/'.join(args.ssap_uri)
    if not args.ssap_uri.startswith('ssap://'):
        args.ssap_uri = 'ssap://' + args.ssap_uri
    
    return args


def main(): 
    """
    Send a single command to TV
    """

    args = parse_args()
    settings = load_settings(args.settings_file)

    if 'ip' not in settings:
        try:
            settings['ip'] = discover_ip_address()
        except:
            print("Unable to discover ip address of TV", file=sys.stderr)
            sys.exit(1)
   
    if args.find_mac_address:
        try:
            settings['mac-address'] = find_mac_address(settings['ip'])
        except:
            print("Unable to find MAC address in arp cache. Ensure the TV is "
                    "on and that arp is installed and on the path.",
                    file=sys.stderr)
            sys.exit(1)
    elif args.wake:
        if 'mac-address' not in settings:
            print("Unable to wake TV: no MAC address saved. "
                    "Run lgtv --find-mac-address with the TV on",
                    file=sys.stderr)
            sys.exit(1)
        wakeonlan.send_magic_packet(settings['mac-address'])
    else: 
        ws_uri = 'ws://' + settings['ip'] + ':3000'
        client_key = settings.get('client-key')

        (response, client_key) = send(ws_uri, args.ssap_uri, args.payload, client_key)

        print(response)

        settings['client-key'] = client_key
    
    save_settings(args.settings_file, settings)
