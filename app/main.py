from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI()

class Cliente(BaseModel):
    nome: str = Field(..., max_length=20)
    tipo_atendimento: str = Field(..., pattern="^[NP]$")
    data_entrada: datetime = Field(default_factory=datetime.now)
    atendido: bool = Field(default=False)
    posicao: int = Field(default=0)

fila: List[Cliente] = []

def atualizar_posicoes():
    prioridade = [c for c in fila if c.tipo_atendimento == "P" and not c.atendido]
    normal = [c for c in fila if c.tipo_atendimento == "N" and not c.atendido]
    todos_nao_atendidos = prioridade + normal

    for idx, cliente in enumerate(todos_nao_atendidos):
        cliente.posicao = idx + 1

@app.get("/fila", response_model=List[Cliente])
def obter_fila():
    if not fila:
        return []
    return [c for c in fila if not c.atendido]

@app.get("/fila/{id}", response_model=Cliente)
def obter_cliente(id: int):
    for cliente in fila:
        if cliente.posicao == id and not cliente.atendido:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente não encontrado na posição especificada.")

@app.post("/fila", response_model=Cliente)
def adicionar_cliente(cliente: Cliente):
    if len(cliente.nome.strip()) == 0:
        raise HTTPException(status_code=400, detail="O campo nome é obrigatório.")
    
    fila.append(cliente)
    atualizar_posicoes()
    return cliente

@app.put("/fila")
def atualizar_fila():
    for cliente in fila:
        if cliente.posicao == 1:
            cliente.posicao = 0
            cliente.atendido = True
    atualizar_posicoes()
    return {"message": "Fila atualizada com sucesso."}

@app.delete("/fila/{id}")
def remover_cliente(id: int):
    for idx, cliente in enumerate(fila):
        if cliente.posicao == id and not cliente.atendido:
            fila.pop(idx)
            atualizar_posicoes()
            return {"message": "Cliente removido com sucesso."}
    raise HTTPException(status_code=404, detail="Cliente não encontrado na posição especificada.")