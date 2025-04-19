#!/usr/bin/env python3

import logging
import os
import signal
import socket
import subprocess
import time

class Runner:
    def __init__(self):
        self.server = None
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

    def run(self):
        while True:
            # low-power idle waiting for players
            logging.info("waiting for connection attempt...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", 7777))
            s.listen()
            (c, addr) = s.accept()
            c.close()
            s.close()
            logging.info(f"attempted connection from {addr}, starting server...")

            # start server
            with open("/root/password.txt", "r") as f:
                password = f.read()
            self.server = subprocess.Popen([
                "/bin/bash",
                "/root/server/start-tModLoaderServer.sh", 
                "-nosteam",
                "-config", "/root/config.txt",
                "-pass", f"{password}",
            ], stdin=subprocess.PIPE, start_new_session=True)
            while not self.started():
                time.sleep(1.0)

            # wait until no connections for timeout
            logging.info("server started, waiting until idle for 30s...")
            idle_start = time.time()
            while (time.time() - idle_start) < 30.0:
                time.sleep(1.0)
                if self.playing():
                    idle_start = time.time()

            # stop server
            self.exit()
            while self.started():
                time.sleep(1.0)

    def started(self):
        return b"LISTEN" in subprocess.check_output([
            "ss", "-tln", "( sport = :7777 )"])

    def playing(self):
        return b"ESTAB" in subprocess.check_output([
            "ss", "-tn", "( sport = :7777 )"])

    def exit(self):
        if self.server:
            logging.info("shutting down server...")
            self.server.stdin.write(b"exit\n")
            self.server.stdin.flush()
            timeout, start = True, time.time()
            while (time.time() - start) < 8.0:
                if self.server.poll() is not None:
                    timeout = False
                    break
                time.sleep(0.25)
            if timeout:
                logging.error("forcefully shutting down server...")
                os.killpg(os.getpgid(self.server.pid), signal.SIGKILL)
        self.server = None

    def terminate(self, signum, frame):
        self.exit()
        exit(0)

if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    runner = Runner()
    runner.run()
