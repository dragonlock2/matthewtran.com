#!/usr/bin/env python3

import hashlib
import subprocess
import sys

DP_LEN  = 64 # xfinity delegated prefix length
WRT_ULA = "fd16:8f4d:f516::" # OpenWrt random
WG_ULA  = "fd32:76a6:ec61:577a::" # WireGuard random
IPV4    = "192.168.1.69" # OpenWrt default
IPV6    = "69"
WG_IPV4 = "192.168.2.1" # WireGuard chosen
WG_IPV6 = WG_ULA + "1"

def run(cmds):
    # ssh-keygen -t ed25519
    subprocess.run(["ssh", "root@OpenWrt.lan", ";".join(cmds)], check=True)

def mac(eth):
    return open(f"/sys/class/net/{eth}/address", "r").read().strip()

def duid():
    # adapted from https://github.com/mss/nm-duid
    id = bytes.fromhex(open("/etc/machine-id", "r").read().strip())
    return "0004" + hashlib.sha256(id).digest()[:16].hex()

def key():
    priv = subprocess.check_output(["wg", "genkey"]).strip()
    pub = subprocess.check_output(["wg", "pubkey"], input=priv).strip()
    return (pub.decode("utf-8"), priv.decode("utf-8"))

if __name__ == "__main__":
    ETH = sys.argv[1] # e.g. enp5s0

    # basic setup
    run([
        f"uci set network.globals.ula_prefix='{WRT_ULA}/48'"
        "uci set dropbear.main.Interface='lan'",
        "uci commit network",
        "uci commit dropbear",
    ])

    # static IP
    run([
        "uci add dhcp host",
        "uci set dhcp.@host[-1].name='matt-ryzen'",
        f"uci set dhcp.@host[-1].mac='{mac(ETH)}'",
        f"uci set dhcp.@host[-1].ip='{IPV4}'",
        f"uci set dhcp.@host[-1].duid='{duid()}'",
        f"uci set dhcp.@host[-1].hostid='{IPV6}'",
        "uci commit dhcp",
        "service dnsmasq restart",
        "service odhcpd restart",
    ])

    # forward traffic
    PORTS = {
        "http"        : "80",
        "https"       : "443",
        "git"         : "2222",
        "monerod"     : "18080-18081",
        "p2pool"      : "3333",
        "p2pool2"     : "37888-37889",
        "minecraft"   : "25565",
        "minecraft_be": "19132-19133",
        "terraria"    : "7777",
    }
    for name in PORTS:
        run([
            # IPv4 port forward
            "uci add firewall redirect",
            f"uci set firewall.@redirect[-1].name='{name}'",
            "uci set firewall.@redirect[-1].target='DNAT'",
            "uci set firewall.@redirect[-1].family='IPv4'",
            "uci set firewall.@redirect[-1].src='wan'",
            f"uci set firewall.@redirect[-1].src_dport='{PORTS[name]}'",
            "uci set firewall.@redirect[-1].dest='lan'",
            f"uci set firewall.@redirect[-1].dest_ip='{IPV4}'",
            f"uci set firewall.@redirect[-1].dest_port='{PORTS[name]}'",

            # IPv6 traffic rules
            "uci add firewall rule",
            f"uci set firewall.@rule[-1].name='allow-{name}'",
            "uci set firewall.@rule[-1].family='ipv6'",
            "uci set firewall.@rule[-1].src='wan'",
            "uci set firewall.@rule[-1].dest='lan'",
            f"uci set firewall.@rule[-1].dest_ip='::{IPV6}/{DP_LEN-128}'",
            f"uci set firewall.@rule[-1].dest_port='{PORTS[name]}'",
            "uci set firewall.@rule[-1].target='ACCEPT'",
        ])
    run([
        "uci commit firewall",
        "service firewall restart",
    ])

    # wireguard setup
    # TODO configure NAT66 to fix tunneling IPv6 traffic
    pub, priv = key()
    run([
        # install packages
        "opkg update",
        "opkg install luci-proto-wireguard",

        # create interface
        "uci set network.wg0=interface",
        "uci set network.wg0.proto='wireguard'",
        f"uci set network.wg0.private_key='{priv}'",
        "uci set network.wg0.listen_port='51820'",
        f"uci add_list network.wg0.addresses='{WG_IPV4}/24'",
        f"uci add_list network.wg0.addresses='{WG_IPV6}/64'",
        "uci commit network",

        # allow traffic
        "uci del firewall.@zone[0].network",
        "uci add_list firewall.@zone[0].network='lan'",
        "uci add_list firewall.@zone[0].network='wg0'",
        "uci add firewall rule",
        "uci set firewall.@rule[-1].name='allow-wireguard'",
        "uci add_list firewall.@rule[-1].proto='udp'",
        "uci set firewall.@rule[-1].src='wan'",
        "uci set firewall.@rule[-1].dest_port='51820'",
        "uci set firewall.@rule[-1].target='ACCEPT'",
        "uci commit firewall",
    ])
