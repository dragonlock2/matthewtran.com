#!/usr/bin/env python3

import time
import urllib.request
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

if __name__ == '__main__':
    sg = SendGridAPIClient(Path('sendgrid.key').read_text())

    old_ipv4, old_ipv6 = None, None
    while True:
        ipv4 = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        ipv6 = urllib.request.urlopen('https://v6.ident.me').read().decode('utf8')

        if ipv4 != old_ipv4 or ipv6 != old_ipv6:
            msg = Mail(
                from_email='matthewlamtran@berkeley.edu',
                to_emails='mtran319@gmail.com',
                subject='pls update ip',
                html_content=f'<p>ipv4: {ipv4}</p><p>ipv6: {ipv6}</p>'
            )
            try:
                print(f'IP changed to {ipv4} and {ipv6}')
                resp = sg.send(msg)
            except Exception as e:
                print(e.message)
                sg = SendGridAPIClient(Path('sendgrid.key').read_text())

        old_ipv4, old_ipv6 = ipv4, ipv6
        time.sleep(60 * 60) # 60 min
