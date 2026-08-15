import sqlite3
import ipaddress

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

def get_valid_port():
    while True:
        try:
            port = int(input("Enter Port: "))

            if 1 <= port <= 65535:
                return port

            print("Invalid port. Enter a number between 1 and 65535.")

        except ValueError:
            print("Invalid port. Please enter a number.")


def get_valid_priority():
    while True:
        try:
            priority = int(input("Enter Priority (1 = highest): "))

            if priority >= 1:
                return priority

            print("Priority must be 1 or higher.")

        except ValueError:
            print("Invalid priority. Please enter a number.")


def get_valid_action():
    while True:
        action = input("Enter Action (ALLOW/BLOCK): ").strip().upper()

        if action in ["ALLOW", "BLOCK"]:
            return action

        print("Invalid action. Please enter ALLOW or BLOCK.")

def get_valid_ip():
    while True:
        ip = input("Enter IP Address: ").strip()

        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            print("Invalid IP address. Please enter a valid IPv4 address.")


def get_valid_protocol():
    while True:
        protocol = input("Enter Protocol: ").strip().upper()

        if protocol in ["TCP", "UDP", "ICMP"]:
            return protocol

        print("Invalid protocol. Use TCP, UDP, or ICMP.")

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
    WHERE ip_address = ? AND port IS NULL AND protocol IS NULL AND action = ?
)
""", (
    1,
    "192.168.1.10",
    None,
    None,
    "BLOCK",

    "192.168.1.10",
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
    print("6. View Statistics")
    print("7. Clear Packet Logs")
    print("8. Exit")

    choice = input("Choose an option: ")

    if choice == "1":

        # Fake network packet
        packet = {
            "ip": get_valid_ip(),
            "port": get_valid_port(),
            "protocol": get_valid_protocol()
        }

        # Check all firewall rules
        cursor.execute("""
        SELECT *
        FROM firewall_rules
        ORDER BY priority ASC
        """)
        rules = cursor.fetchall()

        decision = "ALLOW"
        matched_rules = []

        for rule in rules:
            rule_id, priority, ip, port, protocol, action = rule

            ip_match = (ip is None or ip == packet["ip"])
            port_match = (port is None or port == packet["port"])
            protocol_match = (protocol is None or protocol == packet["protocol"])

            if ip_match and port_match and protocol_match:
                matched_rules.append(rule)

                if action == "BLOCK":
                    decision = "BLOCK"

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
                matched_rules[0][0]
            ))

            conn.commit()

            print("❌ BLOCKED")
            print("Reasons:")

            for rule in matched_rules:
                reason = []

                if rule[2] is not None:
                    reason.append(f"IP {rule[2]}")
                if rule[3] is not None:
                    reason.append(f"Port {rule[3]}")
                if rule[4] is not None:
                    reason.append(f"Protocol {rule[4]}")

                print(f"- Rule #{rule[0]}: {', '.join(reason)} is blocked")

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

        cursor.execute("SELECT * FROM firewall_rules ORDER BY priority ASC")
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
        priority = get_valid_priority()

        ip = input("Enter IP Address (leave blank for ANY): ").strip()
        port = input("Enter Port (leave blank for ANY): ").strip()
        protocol = input("Enter Protocol (leave blank for ANY): ").strip().upper()
        action = get_valid_action()

        if ip == "":
            ip = None
        else:
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                print("Invalid IP address.")
                continue

        if port == "":
            port = None
        else:
            try:
                port = int(port)

                if not 1 <= port <= 65535:
                    print("Invalid port. Enter a number between 1 and 65535.")
                    continue

            except ValueError:
                print("Invalid port. Please enter a number.")
                continue

        if protocol == "":
            protocol = None
        elif protocol not in ["TCP", "UDP", "ICMP"]:
            print("Invalid protocol. Use TCP, UDP, or ICMP.")
            continue

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

        print("\n===== FIREWALL STATISTICS =====")

        cursor.execute("""
        SELECT COUNT(*) FROM packet_logs
        """)
        total_packets = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(*) FROM packet_logs
        WHERE decision = 'ALLOW'
        """)
        allowed_packets = cursor.fetchone()[0]

        cursor.execute("""
        SELECT COUNT(*) FROM packet_logs
        WHERE decision = 'BLOCK'
        """)
        blocked_packets = cursor.fetchone()[0]

        if total_packets == 0:
            print("No packet data available.")
        else:
            allow_rate = (allowed_packets / total_packets) * 100
            block_rate = (blocked_packets / total_packets) * 100

            print(f"Total Packets : {total_packets}")
            print(f"Allowed       : {allowed_packets}")
            print(f"Blocked       : {blocked_packets}")
            print(f"Allow Rate    : {allow_rate:.1f}%")
            print(f"Block Rate    : {block_rate:.1f}%")


    elif choice == "7":
        print("\n===== CLEAR PACKET LOGS =====")
        confirm = input("Are you sure you want to clear all packet logs? (Y/N): ").strip().upper()

        if confirm == "Y":
            cursor.execute("DELETE FROM packet_logs")
            conn.commit()
            print("✅ Packet logs cleared.")
        else:
            print("Packet logs were not cleared.")


    elif choice == "8":
        conn.close()
        print("Exiting firewall simulator...")
        break

    else:
        print("Invalid option.")