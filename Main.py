# Fake network packet
packet = {
    "ip": "192.168.1.10",
    "port": 80,
    "protocol": "TCP"
}

# Firewall rule
blocked_ip = "192.168.1.10"

# Check the packet
if packet["ip"] == blocked_ip:
    print("❌ BLOCKED")
    print("Reason: IP address is blocked.")
else:
    print("✅ ALLOWED")