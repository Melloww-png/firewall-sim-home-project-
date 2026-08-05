import sqlite3

conn = sqlite3.connect("firewall.db") 
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS firewall_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    port INTEGER,
    protocol TEXT,
    action TEXT
)
""")

conn.commit()

cursor.execute("""
INSERT INTO firewall_rules (ip_address, port, protocol, action)
SELECT ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address = ? AND port = ? AND protocol = ? AND action = ?
)
""", (
    "192.168.1.10", 80, "TCP", "BLOCK",
    "192.168.1.10", 80, "TCP", "BLOCK"
))

cursor.execute("""
INSERT INTO firewall_rules (ip_address, port, protocol, action)
SELECT ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address IS NULL AND port = ? AND protocol IS NULL AND action = ?
)
""", (
    None, 23, None, "BLOCK",
    23, "BLOCK"
))

cursor.execute("""
INSERT INTO firewall_rules (ip_address, port, protocol, action)
SELECT ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address IS NULL AND port IS NULL AND protocol = ? AND action = ?
)
""", (
    None, None, "UDP", "BLOCK",
    "UDP", "BLOCK"
))

conn.commit()

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

        # Check all firewall rules
        cursor.execute("SELECT * FROM firewall_rules")
        rules = cursor.fetchall()

        decision = "ALLOW"
        matched_rule = None

        for rule in rules:
            rule_id, ip, port, protocol, action = rule

            ip_match = (ip is None or ip == packet["ip"])
            port_match = (port is None or port == packet["port"])
            protocol_match = (protocol is None or protocol == packet["protocol"])

            if ip_match and port_match and protocol_match:
                decision = action
                matched_rule = rule
                break

        if decision == "BLOCK":
            print("❌ BLOCKED")
            print(f"Matched Rule #{matched_rule[0]}")
            print(f"Action: {matched_rule[4]}")
        else:
            print("✅ ALLOWED")
            print("Reason: No firewall rule matched.")

    elif choice == "2":
        print("\n===== FIREWALL RULES =====")

        cursor.execute("SELECT * FROM firewall_rules")
        rules = cursor.fetchall()

        if not rules:
            print("No firewall rules found.")
        else:
            print(f"{'ID':<5}{'IP Address':<18}{'Port':<8}{'Protocol':<12}{'Action'}")
            print("-" * 55)

            for rule in rules:
                rule_id, ip, port, protocol, action = rule

                print(
                    f"{rule_id:<5}"
                    f"{str(ip) if ip else 'ANY':<18}"
                    f"{str(port) if port else 'ANY':<8}"
                    f"{protocol if protocol else 'ANY':<12}"
                    f"{action}"
                )
    elif choice == "3":
        ip = input("Enter IP to block: ")
        cursor.execute(
            "INSERT OR IGNORE INTO blocked_ips VALUES (?)", 
            (ip,)
        )
        conn.commit()

        print(f"{ip} has been added to the blocked list.")

    elif choice == "4":
        ip = input("Enter IP to remove: ")

        cursor.execute(
            "DELETE FROM blocked_ips WHERE ip_address = ?",
            (ip,)
        )
        conn.commit()

        if cursor.rowcount > 0:
            print(f"{ip} has been removed.")
        else:
            print("IP not found.")


    elif choice == "5":
        conn.close()
        print("Exiting firewall simulator...")
        break

    else:
        print("Invalid option.")