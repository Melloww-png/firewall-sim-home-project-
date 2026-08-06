import sqlite3

conn = sqlite3.connect("firewall.db") 
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS firewall_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority INTEGER,
    ip_address TEXT,
    port INTEGER,
    protocol TEXT,
    action TEXT
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS packet_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    port INTEGER,
    protocol TEXT,
    decision TEXT,
    matched_rule INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

cursor.execute("""
INSERT INTO firewall_rules (priority, ip_address, port, protocol, action)
SELECT ?, ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address = ? AND port = ? AND protocol = ? AND action = ?
)
""", (
    1,
    "192.168.1.10",
    80,
    "ATP",
    "BLOCK",

    "192.168.1.10",
    80,
    "ATP",
    "BLOCK"
))

cursor.execute("""
INSERT INTO firewall_rules (priority, ip_address, port, protocol, action)
SELECT ?, ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address IS NULL AND port = ? AND protocol IS NULL AND action = ?
)
""", (
    2,
    None,
    23,
    None,
    "BLOCK",

    23,
    "BLOCK"
))

cursor.execute("""
INSERT INTO firewall_rules (priority, ip_address, port, protocol, action)
SELECT ?, ?, ?, ?, ?
WHERE NOT EXISTS (
    SELECT 1 FROM firewall_rules
    WHERE ip_address IS NULL AND port IS NULL AND protocol = ? AND action = ?
)
""", (
    3,
    None,
    None,
    "UDP",
    "BLOCK",

    "UDP",
    "BLOCK"
))

conn.commit()


while True:

    print("\n===== FIREWALL SIMULATOR =====")
    print("1. Check Packet")
    print("2. View Firewall Rules")
    print("3. Add Firewall Rule")
    print("4. Delete Firewall Rule")
    print("5. View Packet Logs")
    print("6. Exit")

    choice = input("Choose an option: ")

    if choice == "1":

        # Fake network packet
        packet = {
            "ip": input("Enter IP Address: "),
            "port": int(input("Enter Port: ")),
            "protocol": input("Enter Protocol: ").upper()
        }

        # Check all firewall rules
        cursor.execute("""
        SELECT *
        FROM firewall_rules
        ORDER BY priority ASC
        """)
        rules = cursor.fetchall()

        decision = "ALLOW"
        matched_rule = None

        for rule in rules:
            rule_id, priority, ip, port, protocol, action = rule

            ip_match = (ip is None or ip == packet["ip"])
            port_match = (port is None or port == packet["port"])
            protocol_match = (protocol is None or protocol == packet["protocol"])

            if ip_match and port_match and protocol_match:
                decision = action
                matched_rule = rule
                break

        if decision == "BLOCK":
            cursor.execute("""
            INSERT INTO packet_logs
            (ip_address, port, protocol, decision, matched_rule)
            VALUES (?, ?, ?, ?, ?)
            """, (
                packet["ip"],
                packet["port"],
                packet["protocol"],
                "BLOCK",
                matched_rule[0]
            ))

            conn.commit()

            print("❌ BLOCKED")
            print(f"Matched Rule #{matched_rule[0]}")
            print(f"Action: {matched_rule[5]}")
        else:
            cursor.execute("""
            INSERT INTO packet_logs
            (ip_address, port, protocol, decision, matched_rule)
            VALUES (?, ?, ?, ?, ?)
            """, (
                packet["ip"],
                packet["port"],
                packet["protocol"],
                "ALLOW",
                None
            ))

            conn.commit()

            print("✅ ALLOWED")
            print("Reason: No firewall rule matched.")


    elif choice == "2":
        print("\n===== FIREWALL RULES =====")

        cursor.execute("SELECT * FROM firewall_rules")
        rules = cursor.fetchall()

        if not rules:
            print("No firewall rules found.")
        else:
            print(f"{'Priority':<10}{'ID':<5}{'IP Address':<18}{'Port':<8}{'Protocol':<12}{'Action'}")
            print("-" * 55)

            for rule in rules:
                rule_id, priority, ip, port, protocol, action = rule
                print(
                    f"{priority:<10}"
                    f"{rule_id:<5}"
                    f"{str(ip) if ip else 'ANY':<18}"
                    f"{str(port) if port else 'ANY':<8}"
                    f"{protocol if protocol else 'ANY':<12}"
                    f"{action}"
                )


    elif choice == "3":
        print("\n===== ADD FIREWALL RULE =====")
        priority = int(input("Enter Priority (1 = highest): "))

        ip = input("Enter IP Address (leave blank for ANY): ").strip()
        port = input("Enter Port (leave blank for ANY): ").strip()
        protocol = input("Enter Protocol (leave blank for ANY): ").strip().upper()
        action = input("Enter Action (ALLOW/BLOCK): ").strip().upper()

        # Convert blank inputs to None (ANY)
        if ip == "":
            ip = None

        if port == "":
            port = None
        else:
            port = int(port)

        if protocol == "":
            protocol = None

        # Validate the action
        if action not in ["ALLOW", "BLOCK"]:
            print("Invalid action. Please enter ALLOW or BLOCK.")
        else:
            cursor.execute("""
            INSERT INTO firewall_rules
            (priority, ip_address, port, protocol, action)
            VALUES (?, ?, ?, ?, ?)
            """, (priority, ip, port, protocol, action))

            conn.commit()

        print("✅ Firewall rule added successfully!")


    elif choice == "4":
        print("\n===== DELETE FIREWALL RULE =====")

        rule_id = input("Enter Rule ID to delete: ")

        try:
            rule_id = int(rule_id)

            cursor.execute(
                "DELETE FROM firewall_rules WHERE id = ?",
                (rule_id,)
            )
            conn.commit()

            if cursor.rowcount > 0:
                print(f"✅ Rule #{rule_id} has been deleted.")
            else:
                print("❌ Rule ID not found.")

        except ValueError:
            print("Please enter a valid Rule ID.")

    elif choice == "5":

        print("\n===== PACKET LOGS =====")

        cursor.execute("""
        SELECT id, timestamp, ip_address, port, protocol, decision, matched_rule
        FROM packet_logs
        ORDER BY id DESC
        """)

        logs = cursor.fetchall()

        if not logs:
            print("No packet logs found.")
        else:
            print(f"{'ID':<5}{'Time':<22}{'IP Address':<18}{'Port':<8}{'Protocol':<10}{'Decision':<10}{'Rule'}")
            print("-" * 90)

            for log in logs:
                log_id, time, ip, port, protocol, decision, rule = log

                print(
                    f"{log_id:<5}"
                    f"{time:<22}"
                    f"{ip:<18}"
                    f"{port:<8}"
                    f"{protocol:<10}"
                    f"{decision:<10}"
                    f"{rule if rule else '-'}"
                )


    elif choice == "6":
        conn.close()
        print("Exiting firewall simulator...")
        break

    else:
        print("Invalid option.")