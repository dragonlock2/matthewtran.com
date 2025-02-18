#!/usr/bin/env python3

import time
import urllib.request
from ipaddress import ip_network
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

if __name__ == "__main__":
    sg = SendGridAPIClient(Path("sendgrid.key").read_text())

    old_ipv4, old_ipv6 = None, None
    while True:
        try:
            ipv4 = urllib.request.urlopen("https://v4.ident.me").read().decode("utf8")
            ipv6 = urllib.request.urlopen("https://v6.ident.me").read().decode("utf8")
            ipv6 = str(ip_network(ipv6 + "/64", strict=False).network_address) # xfinity gives /64
        except Exception as e:
            print(e)
            time.sleep(60)
            continue

        if ipv4 != old_ipv4 or ipv6 != old_ipv6:
            msg = Mail(
                from_email="mtran319@gmail.com",
                to_emails="mtran319@gmail.com",
                subject="pls update ip",
                html_content=f"<p>old ipv4: {old_ipv4}</p>"
                             f"<p>old ipv6: {old_ipv6}</p>"
                             f"<p>new ipv4: {ipv4}</p>"
                             f"<p>new ipv6: {ipv6}</p>"
            )
            try:
                print(f"IP changed to {ipv4} and {ipv6}")
                resp = sg.send(msg)
            except Exception as e:
                print(e)
                sg = SendGridAPIClient(Path("sendgrid.key").read_text())
                time.sleep(60)
                continue

        old_ipv4, old_ipv6 = ipv4, ipv6
        time.sleep(3600)
