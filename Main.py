import sqlite3

conn = sqlite3.connect("firewall.db") 
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_ips (
    ip_address TEXT PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_ports (
    port INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_protocols (
    protocol TEXT PRIMARY KEY
)
""")

conn.commit()

cursor.execute("INSERT OR IGNORE INTO blocked_ips VALUES (?)", ("192.168.1.10",))
cursor.execute("INSERT OR IGNORE INTO blocked_ips VALUES (?)", ("10.0.0.5",))

cursor.execute("INSERT OR IGNORE INTO blocked_ports VALUES (?)", (23,))
cursor.execute("INSERT OR IGNORE INTO blocked_ports VALUES (?)", (21,))

cursor.execute("INSERT OR IGNORE INTO blocked_protocols VALUES (?)", ("UDP",))

conn.commit()

print("Blocked IPs in database:")

cursor.execute("SELECT * FROM blocked_ips")

for row in cursor.fetchall():
    print(row)

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

        cursor.execute(
            "SELECT * FROM blocked_ips WHERE ip_address = ?", 
            (packet["ip"],)
        )
        
        if cursor.fetchone():
            blocked_reasons.append("IP Address")

        cursor.execute(
            "SELECT * FROM blocked_ports WHERE port = ?",
            (packet["port"],)
        )

        if cursor.fetchone():
            blocked_reasons.append("Port")

        cursor.execute(
            "SELECT * FROM blocked_protocols WHERE protocol = ?",
            (packet["protocol"],)
        )

        if cursor.fetchone():
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
        print("\nBlocked IPs:")
        cursor.execute("SELECT * FROM blocked_ips")
        for row in cursor.fetchall():
            print(row[0])

        print("Blocked Ports:")
        cursor.execute("SELECT * FROM blocked_ports")
        for row in cursor.fetchall():
            print(row[0])

        print("Blocked Protocols:")
        cursor.execute("SELECT * FROM blocked_protocols")
        for row in cursor.fetchall():
            print(row[0])

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
        print("Exiting firewall simulator...")
        break

    else:
        print("Invalid option.")