import psycopg2

host = 'localhost'
port = '5432'
dbname = 'postgres'
user = 'postgres'
password = 'AMWTech.2023'

conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
print("Connection successful!")

cur = conn.cursor()
cur.execute("""
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keywords VARCHAR(255) NOT NULL)
""")
conn.commit()

cur1 = conn.cursor()
cur1.execute("""
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    roberta_score VARCHAR(255) NOT NULL)
""")

conn.commit()

conn.close()
