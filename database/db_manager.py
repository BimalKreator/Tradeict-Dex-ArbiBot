import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    with open("database/schema.sql", "r", encoding="utf-8") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()


def save_token_mapping(symbol, network, contract_address, liquidity):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO token_mappings (symbol, network, contract_address, liquidity)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (network, contract_address) DO NOTHING
        """,
        (symbol, network, contract_address, liquidity),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_mapped_addresses(symbol):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT contract_address
        FROM token_mappings
        WHERE LOWER(symbol) = LOWER(%s)
        """,
        (symbol,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]