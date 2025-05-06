#!/usr/bin/env python3

import requests
import time
from ipaddress import ip_network
from pathlib import Path

if __name__ == "__main__":
    link = Path("discord.txt").read_text()

    old_ipv4, old_ipv6 = None, None
    while True:
        # get current ips
        try:
            ipv4 = requests.get("https://v4.ident.me").text
            ipv6 = requests.get("https://v6.ident.me").text
            ipv6 = str(ip_network(ipv6 + "/64", strict=False).network_address) # xfinity gives /64
        except Exception as e:
            print("Error while getting IP", e)
            time.sleep(60)
            continue

        # send message if either changed
        if ipv4 != old_ipv4 or ipv6 != old_ipv6:
            try:
                print(f"IP changed to {ipv4} and {ipv6}")
                resp = requests.post(link, json={
                    "content": "\n".join([
                        f"old ipv4: {old_ipv4}",
                        f"old ipv6: {old_ipv6}",
                        f"new ipv4: {ipv4}",
                        f"new ipv6: {ipv6}",
                    ])
                })
                assert(resp.status_code == 204)
            except Exception as e:
                print("Error while sending update", e)
                time.sleep(60)
                continue

        # retry every hour
        print("Retrying in 1 hour...")
        old_ipv4, old_ipv6 = ipv4, ipv6
        time.sleep(3600)
