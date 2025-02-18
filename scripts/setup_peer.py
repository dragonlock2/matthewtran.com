#!/usr/bin/env python3

import subprocess
import sys
from ipaddress import ip_address, ip_network
from setup_router import WG_IPV4, WG_IPV6, run, key

def ips():
    try:
        ret = subprocess.check_output(["ssh", "root@OpenWrt.lan", "uci get network.@wireguard_wg0[-1].allowed_ips"]).decode("utf-8")
        ipv4, ipv6 = ret.split()
        ipv4, ipv6 = ipv4.split("/")[0], ipv6.split("/")[0]
    except subprocess.CalledProcessError:
        ipv4, ipv6 = WG_IPV4, WG_IPV6
    net4, net6 = ip_network(ipv4 + "/24", strict=False), ip_network(ipv6 + "/64", strict=False)
    ipv4, ipv6 = ip_address(ipv4), ip_address(ipv6)
    if (ipv4 + 1) in net4 and (ipv6 + 1) in net6:
        return str(ipv4 + 1), str(ipv6 + 1)
    raise Exception("no ips left")

if __name__ == "__main__":
    name = sys.argv[1]
    ipv4, ipv6 = ips()
    pub, priv = key()
    run([
        "uci add network wireguard_wg0",
        f"uci set network.@wireguard_wg0[-1].description='{name}'",
        f"uci set network.@wireguard_wg0[-1].public_key='{pub}'",
        f"uci set network.@wireguard_wg0[-1].private_key='{priv}'",
        f"uci add_list network.@wireguard_wg0[-1].allowed_ips='{ipv4}/32'",
        f"uci add_list network.@wireguard_wg0[-1].allowed_ips='{ipv6}/128'",
        "uci set network.@wireguard_wg0[-1].endpoint_host='wg.matthewtran.com'",
        "uci set network.@wireguard_wg0[-1].endpoint_port='51820'",
        "uci set network.@wireguard_wg0[-1].persistent_keepalive='25'",
        "uci commit network",
        "ifdown wg0",
        "ifup wg0",
    ])
    print("Go to the following to generate configuration, double check endpoint:")
    print(f"Network > Interfaces > wg0 (Edit) > Peers > {name} (Edit) > Generate configuration...")
