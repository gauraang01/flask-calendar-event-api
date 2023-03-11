import psycopg2

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host="34.121.82.29",
    port=5432,
    dbname="calendar_service_db",
    user="postgres",
    password="wow@9WOW"
)

# Create a cursor object
cur = conn.cursor()

# # Define the SQL commands to create the tables
# create_users_table = """
#      CREATE TABLE IF NOT EXISTS Users (
#     id SERIAL PRIMARY KEY,
#     google_id VARCHAR(255) NOT NULL,
#     name VARCHAR(255) NOT NULL,
#     access_token TEXT NOT NULL
# );"""

create_tokens_table = """
   CREATE TABLE IF NOT EXISTS Tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES Users(id) ON DELETE CASCADE,
        access_token TEXT NOT NULL,
        refresh_token TEXT NOT NULL,
        expires_in INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        CONSTRAINT unique_user_id_tokens UNIQUE (user_id)
    );
"""


create_events_table = """
    CREATE TABLE IF NOT EXISTS Calendar (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(id) ON DELETE CASCADE,
    event_id VARCHAR(255) NOT NULL,
    event_start TIMESTAMP NOT NULL,
    event_end TIMESTAMP NOT NULL,
    event_summary VARCHAR(255),
    event_description TEXT
    );
"""


# Execute the SQL commands
cur.execute("ALTER TABLE Tokens ADD CONSTRAINT tokens_user_id_unique UNIQUE (user_id);")
# cur.execute(create_tokens_table)
# cur.execute(create_events_table)

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
