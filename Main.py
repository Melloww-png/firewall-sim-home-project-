# Fake network packet
packet = {
    "ip": "192.168.1.10",
    "port": 23,
    "protocol": "TCP"
}

# Firewall rules
blocked_ips = ["192.168.1.10", "10.0.0.5"]
blocked_ports = [23, 21]

# Check the packet
if packet["ip"] in blocked_ips:
    print("❌ BLOCKED")
    print("Reason: IP address is blocked.")

elif packet["port"] in blocked_ports:
    print("❌ BLOCKED")
    print("Reason: Port is blocked.")

else:
    print("✅ ALLOWED")
