#!/usr/bin/env python3

import subprocess
import time

if __name__ == '__main__':
    while True:
        # try renew once a day
        subprocess.run(['certbot', 'renew', '--quiet'])
        time.sleep(86400)
