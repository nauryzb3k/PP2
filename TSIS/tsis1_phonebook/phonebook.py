from connection import get_connection
import json

conn = get_connection()
cur = conn.cursor()

# ==================MENU - SHOW CONTACTS====================================
def show_contacts():
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday,
               g.name, p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
    """)

    rows = cur.fetchall()

    print("\n=== CONTACTS ===")
    for r in rows:
        print(r)

# ==================MENU - SEARCH CONTACTS===================================
def search_contact():
    text = input("Enter name/email/phone: ")

    cur.execute("""
        SELECT c.name, c.email, p.phone
        FROM contacts c
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE c.name ILIKE %s
           OR c.email ILIKE %s
           OR p.phone ILIKE %s
    """, (f"%{text}%", f"%{text}%", f"%{text}%"))

    rows = cur.fetchall()

    for r in rows:
        print(r)

# ==================MENU - ADD CONTACT=======================================
def add_contact():
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD or empty): ")
    group_id = input("Group ID (1 - Family, 2 - Work, 3 - Friend, 4 - Other): ")

    phone = input("Phone: ")
    phone_type = input("Type (Home/Work/Mobile): ")


    cur.execute("""
        INSERT INTO contacts (name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (name, email, birthday if birthday else None,
          group_id if group_id else None))

    contact_id = cur.fetchone()[0]


    cur.execute("""
        INSERT INTO phones (contact_id, phone, type)
        VALUES (%s, %s, %s)
    """, (contact_id, phone, phone_type))

    conn.commit()

    print("Contact added successfully!")

# ===================MENU - FILTER BY GROUP===============================
def filter_by_group():
    group_id = input("Enter group ID (1-Family, 2-Work, 3-Friend, 4-Other): ")

    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.group_id = %s
    """, (group_id,))

    rows = cur.fetchall()

    print("\n=== FILTERED CONTACTS ===")
    for r in rows:
        print(r)

# ===================MENU - SORT CONTACTS=================================
def sort_contacts():
    print("""
Sort by:
1 - Name
2 - Birthday
3 - Date added
""")

    choice = input("Choose option: ")

    if choice == "1":
        order_by = "c.name"
    elif choice == "2":
        order_by = "c.birthday"
    elif choice == "3":
        order_by = "c.date_added"
    else:
        print("Invalid choice")
        return

    cur.execute(f"""
        SELECT c.id, c.name, c.email, c.birthday, c.date_added, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_by} ASC
    """)

    rows = cur.fetchall()

    print("\n=== SORTED CONTACTS ===")
    for r in rows:
        print(r)

# ===================MENU - PAGINATION====================================
def paginate_contacts():
    limit = 2
    offset = 0

    while True:
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            ORDER BY c.id
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()

        print("\n=== CONTACTS PAGE ===")
        for r in rows:
            print(r)

        print("\n[n] next | [p] prev | [q] quit")
        action = input("Choose: ")

        if action == "n":
            offset += limit
        elif action == "p" and offset > 0:
            offset -= limit
        elif action == "q":
            break
        else:
            print("Invalid option")

# ===================MENU - EXPORT TO JSON================================
def export_to_json():
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)

    contacts = cur.fetchall()

    data = []

    for c in contacts:
        contact_id = c[0]

        cur.execute("""
            SELECT phone, type
            FROM phones
            WHERE contact_id = %s
        """, (contact_id,))

        phones = cur.fetchall()

        data.append({
            "id": c[0],
            "name": c[1],
            "email": c[2],
            "birthday": str(c[3]),
            "group": c[4],
            "phones": [{"phone": p[0], "type": p[1]} for p in phones]
        })

    with open("contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("Export completed to contacts.json")

# ===================MENU - IMPORT JSON===================================
def import_from_json():
    with open("contacts.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for c in data:
        name = c["name"]

        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            print(f"⚠ Contact {name} exists. Skip (s) or overwrite (o)?")
            choice = input().lower()

            if choice == "s":
                continue

            elif choice == "o":
                cur.execute("DELETE FROM contacts WHERE name = %s", (name,))

        # get group id
        cur.execute("SELECT id FROM groups WHERE name = %s", (c["group"],))
        group = cur.fetchone()

        group_id = group[0] if group else None

        # insert contact
        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (c["name"], c["email"], c["birthday"], group_id))

        contact_id = cur.fetchone()[0]

        # insert phones
        for p in c["phones"]:
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, p["phone"], p["type"]))

    conn.commit()
    print("✅ Import completed")

# ===================MENU - ADD PHONE=====================================
def add_phone():
    name = input("Enter name: ")
    phone = input("Enter phone: ")
    phone_type = input("Enter type: ")

    cur.execute(
        "CALL add_phone(%s, %s, %s)",
        (name, phone, phone_type)
    )
    conn.commit()

# ===================MENU - MOVE TO GROUP=================================
def move_to_group():
    name = input("Enter contact name: ")
    group_name = input("Enter new group: ")

    cur.execute(
        "CALL move_to_group(%s, %s)",
        (name, group_name)
    )
    conn.commit()

# ===================MENU SEARCH==========================================
def db_search():
    text = input("Enter search text: ")

    cur.execute(
        "SELECT * FROM search_contacts(%s)",
        (text,)
    )

    rows = cur.fetchall()

    for r in rows:
        print(r)

# ===================MAIN MENU============================================
def menu():
    while True:
        print("\n=== PHONEBOOK ===")
        print("1. Show contacts")
        print("2. Search contact")
        print("3. Add contact")
        print("4. Filter by group")
        print("5. Sort contacts")
        print("6. Paginate contacts")
        print("7. Export contacts to JSON")
        print("8. Import from JSON")
        print("9. Add phone to contact")
        print("10. Move contact to group")
        print("q to quit")
        
        choice = input("Choose: ")

        if choice == "1":
            show_contacts()
        elif choice == "2":
            search_contact()
        elif choice == "3":
            add_contact()
        elif choice == "4":
            filter_by_group()
        elif choice == "5":
            sort_contacts()
        elif choice == "6":
            paginate_contacts()
        elif choice == "7":
            export_to_json()
        elif choice == "8":
            import_from_json()
        elif choice == "9":
            add_phone()
        elif choice == "10":
            move_to_group()
        elif choice == "q":
            break

menu()
conn.close()