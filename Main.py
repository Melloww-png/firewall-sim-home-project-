# Firewall rules
blocked_ips = ["192.168.1.10", "10.0.0.5"]
blocked_ports = [23, 21]
blocked_protocols = ["UDP"]

while True:

    print("\n===== FIREWALL SIMULATOR =====")
    print("1. Check Packet")
    print("2. View Firewall Rules")
    print("3. Add Blocked IP")
    print("4. Remove Blocked IP")
    print("5. Exit")

    choice = input("Choose an option: ")

    if choice == "1":

        # Fake network packet
        packet = {
            "ip": input("Enter IP Address: "),
            "port": int(input("Enter Port: ")),
            "protocol": input("Enter Protocol: ").upper()
        }

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

    elif choice == "2":
        print("\nBlocked IPs:", blocked_ips)
        print("Blocked Ports:", blocked_ports)
        print("Blocked Protocols:", blocked_protocols)

    elif choice == "3":
        ip = input("Enter IP to block: ")
        blocked_ips.append(ip)
        print(f"{ip} has been added to the blocked list.")

    elif choice == "4":
        ip = input("Enter IP to remove: ")

        if ip in blocked_ips:
            blocked_ips.remove(ip)
            print(f"{ip} has been removed.")
        else:
            print("IP not found.")

    elif choice == "5":
        print("Exiting firewall simulator...")
        break

    else:
        print("Invalid option.")