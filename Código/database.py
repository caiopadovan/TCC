from sqlalchemy import create_engine, text

# --- Configurações do banco ---
host = ""
port = ""
database = ""
user = ""
password = "%"

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
