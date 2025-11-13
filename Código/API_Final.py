#imports 
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import text
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from database import engine
from autorizacao import autenticar_usuario, criar_token, verificar_token
from pydantic import BaseModel
import json
from pathlib import Path
# criação das classes para importar para o banco de dados
class Cliente(BaseModel):
    nome: str
    email: str
    senha_hash: str
    cpf: Optional[str] = None
    placa: str
    frame: Optional[int] = None
    confianca: Optional[float] = None
    saldo: float = 0.0


class Leitura(BaseModel):
    placa: str
    frame: Optional[int] = None
    confianca: Optional[float] = None
    localizacao:  str = "Ribeirão Preto"


class Cobranca(BaseModel):
    placa: str
    leitura_id: Optional[int] = None
    valor: float
    tipo: str = "Passagem"

#criação do app de para a fast API
app = FastAPI(title="API de Reconhecimento de Placas e Cobranças")



#segurança e criação de token para autenticação 
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not autenticar_usuario(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")

    access_token_expires = timedelta(minutes=60)
    access_token = criar_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

#página inicial API 
@app.get("/")
def root():
    return {"status": "API de Reconhecimento de Placas rodando!"}



#inserir na tabela clientes 
@app.post("/clientes/", dependencies=[Depends(verificar_token)])
def inserir_cliente(cliente: Cliente):
    try:
        with engine.begin() as conn:
            query = text("""
                INSERT INTO clientes (nome, email, senha_hash, cpf, placa, frame, confianca, saldo)
                VALUES (:nome, :email, :senha_hash, :cpf, :placa, :frame, :confianca, :saldo)
                ON CONFLICT (placa) DO UPDATE
                SET nome = EXCLUDED.nome,
                    email = EXCLUDED.email,
                    senha_hash = EXCLUDED.senha_hash,
                    cpf = EXCLUDED.cpf,
                    frame = EXCLUDED.frame,
                    confianca = EXCLUDED.confianca,
                    saldo = EXCLUDED.saldo;
            """)
            conn.execute(query, cliente.model_dump())

        return {"status": "sucesso", "mensagem": f"Cliente {cliente.nome} inserido/atualizado!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#buscar clientes no banco
@app.get("/clientes", dependencies=[Depends(verificar_token)])
def listar_clientes():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM clientes ORDER BY id ASC"))
        clientes = [dict(row._mapping) for row in result]
    return clientes
#postar as leituras enviadas pelo arquivo json e atualizar as cobranças no banco
@app.post("/leituras/")
def inserir_leituras(leituras: list[Leitura]):
    try:
        with engine.begin() as conn:
            inseridos = 0
            ignorados = 0
            cobrancas = 0

            for leitura in leituras:
                # Verifica se a placa pertence a um cliente
                cliente = conn.execute(
                    text("SELECT id, saldo FROM clientes WHERE placa = :placa"),
                    {"placa": leitura.placa}
                ).fetchone()

                if not cliente:
                    ignorados += 1
                    continue

                # Insere leitura
                
                leitura_result = conn.execute(text("""
                INSERT INTO leituras (placa, frame, confianca, horario, localizacao)
                 VALUES (:placa, :frame, :confianca, NOW(), :localizacao)
                 RETURNING id
                    """), {
                    "placa": leitura.placa,
                    "frame": leitura.frame,
                    "confianca": leitura.confianca,
                    "localizacao": "Ribeirão Preto"
                    })
                leitura_id = leitura_result.scalar()


                # Valor fixo do pedágio
                valor_pedagio = 8.50

                # Atualiza saldo
                conn.execute(text("""
                    UPDATE clientes
                    SET saldo = saldo - :valor
                    WHERE placa = :placa
                """), {"valor": valor_pedagio, "placa": leitura.placa})

                # Cria registro de cobrança
                conn.execute(text("""
                    INSERT INTO cobrancas (placa, leitura_id, valor, tipo, data_cobranca)
                    VALUES (:placa, :leitura_id, :valor, 'Pedágio automático', NOW())
                """), {
                    "placa": leitura.placa,
                    "leitura_id": leitura_id,
                    "valor": valor_pedagio
                })

                inseridos += 1
                cobrancas += 1

            return {
                "status": "sucesso",
                "leituras_inseridas": inseridos,
                "leituras_ignoradas": ignorados,
                "cobrancas_realizadas": cobrancas
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#retorna a lista de leituras 
@app.get("/leituras", dependencies=[Depends(verificar_token)])
def listar_leituras():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM leituras ORDER BY id DESC"))
        leituras = [dict(row._mapping) for row in result]
    return leituras


#lista de cobrancas
@app.get("/cobrancas", dependencies=[Depends(verificar_token)])
def listar_cobrancas():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT cb.id, cl.nome AS cliente, cb.placa, cb.valor, cb.tipo, cb.data_cobranca
            FROM cobrancas cb
            JOIN clientes cl ON cb.placa = cl.placa
            ORDER BY cb.id DESC
        """))
        cobrancas = [dict(row._mapping) for row in result]
    return cobrancas
