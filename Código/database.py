from sqlalchemy import create_engine, text

# --- Configurações do banco ---
host = ""       # IP da rede
port = ""       # Porta
database = ""   # Database do banco
user = ""       # Usuário
password = ""   # Senha

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
