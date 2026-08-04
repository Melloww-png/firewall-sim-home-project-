while True:

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

    # reasons for blocking
    blocked_reasons = []

    if packet["ip"] in blocked_ips:
        blocked_reasons.append("IP address")

    if packet["port"] in blocked_ports:
        blocked_reasons.append("Port")

    if packet["protocol"] in blocked_protocols:
        blocked_reasons.append("Protocol")

    # final decision
    if blocked_reasons:
        if len(blocked_reasons) == 1:
            reason = blocked_reasons[0]
        elif len(blocked_reasons) == 2:
            reason = " and ".join(blocked_reasons)
        else:
            reason = ", ".join(blocked_reasons[:-1]) + " and " + blocked_reasons[-1]

        print("❌ BLOCKED")
        print(f"Reason: {reason} blocked.")
    else:
        print("✅ ALLOWED")
        print("Reason: No firewall rules matched.")

    again = input("\nCheck another packet? (y/n): ").lower()
    if again != "y":
        break