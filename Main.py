# Fake network packet
packet = {
    "ip": input("Enter IP Address: "),
    "port": int(input("Enter Port: ")),
    "protocol": input("Enter Protocol: ").upper()
}

# Firewall rules
blocked_ips = ["192.168.1.10", "10.0.0.5"]
blocked_ports = [23, 21]
blocked_protocols = ["UDP"]

# Checking the packet
if packet["ip"] in blocked_ips:
    print("❌ BLOCKED")
    print("Reason: IP address is blocked.")

elif packet["port"] in blocked_ports:
    print("❌ BLOCKED")
    print("Reason: Port is blocked.")

elif packet["protocol"] in blocked_protocols:
    print("❌ BLOCKED")
    print("Reason: Protocol is blocked.")   

else:
    print("✅ ALLOWED")
