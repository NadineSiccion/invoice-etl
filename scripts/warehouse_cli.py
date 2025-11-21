import sqlite3
import os
import re
import sys
# import readline  # optional, for better command-line editing (works on Windows via pyreadline3)

DB_PATH = "warehouse.db"

# --- SECURITY: Disallow modification commands
DISALLOWED_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|PRAGMA|ATTACH|DETACH|VACUUM|TRUNCATE)\b",
    re.IGNORECASE
)

def safe_query(query: str) -> bool:
    """Return False if query contains unsafe keywords."""
    return not DISALLOWED_PATTERNS.search(query)

def main():
    # Ensure the file exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file '{DB_PATH}' not found.")
        sys.exit(1)

    print(f"📦 Connected to '{DB_PATH}' (read-only mode)")
    print("Type your SQL query below. Type 'exit' to quit.\n")

    # Open SQLite in read-only mode
    uri = f"file:{DB_PATH}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as e:
        print(f"❌ Failed to open database: {e}")
        sys.exit(1)

    cursor = conn.cursor()

    while True:
        try:
            query = input("sqlite> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", ".exit", "quit", ".quit"):
                print("👋 Exiting CLI.")
                break

            if not safe_query(query):
                print("⚠️ Error: Write or schema-altering operations are not allowed in read-only mode.")
                continue

            # Execute query
            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                if rows:
                    # Print results in tabular format
                    col_names = [desc[0] for desc in cursor.description]
                    print(" | ".join(col_names))
                    print("-" * (len(" | ".join(col_names))))
                    for row in rows:
                        print(" | ".join(str(x) for x in row))
                else:
                    print("(No results)")

            except sqlite3.Error as e:
                print(f"⚠️ SQLite error: {e}")

        except KeyboardInterrupt:
            print("\n(Use 'exit' to quit)")
        except EOFError:
            print("\n✅ Exiting CLI.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")

    conn.close()


if __name__ == "__main__":
    main()
