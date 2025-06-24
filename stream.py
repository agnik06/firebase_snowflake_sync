import firebase_admin
from firebase_admin import credentials, firestore
import snowflake.connector

# Firebase Admin SDK initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Snowflake credentials
conn = snowflake.connector.connect(
    user="AGNIK",
    password="Agnik-Banerjee123@",
    account="bftitfk-wlb75433",  # e.g., abcd-xy12345.ap-south-1
    warehouse="DOC_AI_QS_WH",
    database="DOC_AI_QS_DB",
    schema="DOC_AI_SCHEMA"
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS USER_ROLES (
    email STRING PRIMARY KEY,
    role STRING
);
""")

# Fetch user roles from Firestore
users_ref = db.collection("user_roles")
docs = users_ref.stream()

# Sync to Snowflake
for doc in docs:
    data = doc.to_dict()
    email = data.get("email")
    role = data.get("role", "user")
    if email:
        cursor.execute(
            "MERGE INTO USER_ROLES t USING (SELECT %s AS email, %s AS role) s "
            "ON t.email = s.email WHEN MATCHED THEN UPDATE SET role = s.role "
            "WHEN NOT MATCHED THEN INSERT (email, role) VALUES (s.email, s.role)",
            (email, role)
        )

cursor.close()
conn.close()
print("User roles synced to Snowflake.")
