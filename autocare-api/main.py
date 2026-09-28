from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException

from database import SessionLocal
from models import Veiculo, Manutencao

from datetime import datetime


app = FastAPI(
    title="AutoCare API",
    description="API do sistema AutoCare",
    version="0.1.0"
)


# Modelo dos dados recebidos pela API
class VeiculoCreate(BaseModel):
    marca: str
    modelo: str
    ano: int
    quilometragem: int
    combustivel: str
    historico_desconhecido: bool = True

class ManutencaoCreate(BaseModel):
    veiculo_id: int
    tipo: str
    data: str
    quilometragem: int
    descricao: str | None = None
    valor: float | None = None


# Cria uma conexão com o banco para cada requisição
def obter_banco():
    banco = SessionLocal()

    try:
        yield banco
    finally:
        banco.close()


# Rota inicial
@app.get("/")
def root():
    return {
        "message": "AutoCare API está funcionando!"
    }


# Cadastrar veículo
@app.post("/veiculos")
def cadastrar_veiculo(
    veiculo: VeiculoCreate,
    banco: Session = Depends(obter_banco)
):
    novo_veiculo = Veiculo(
        marca=veiculo.marca,
        modelo=veiculo.modelo,
        ano=veiculo.ano,
        quilometragem=veiculo.quilometragem,
        combustivel=veiculo.combustivel
    )

    banco.add(novo_veiculo)
    banco.commit()
    banco.refresh(novo_veiculo)

    return {
        "message": "Veículo cadastrado com sucesso!",
        "veiculo": {
            "id": novo_veiculo.id,
            "marca": novo_veiculo.marca,
            "modelo": novo_veiculo.modelo,
            "ano": novo_veiculo.ano,
            "quilometragem": novo_veiculo.quilometragem,
            "combustivel": novo_veiculo.combustivel
        }
    }

@app.get("/veiculos")
def listar_veiculos(
    banco: Session = Depends(obter_banco)
):
    veiculos = banco.query(Veiculo).all()

    return veiculos

@app.get("/veiculos/{id}")
def buscar_veiculo(
    id: int,
    banco: Session = Depends(obter_banco)
):
    veiculo = banco.query(Veiculo).filter(Veiculo.id == id).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    return veiculo

@app.put("/veiculos/{id}")
def atualizar_veiculo(
    id: int,
    dados: VeiculoCreate,
    banco: Session = Depends(obter_banco)
):
    veiculo = banco.query(Veiculo).filter(Veiculo.id == id).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    veiculo.marca = dados.marca
    veiculo.modelo = dados.modelo
    veiculo.ano = dados.ano
    veiculo.quilometragem = dados.quilometragem
    veiculo.combustivel = dados.combustivel

    banco.commit()
    banco.refresh(veiculo)

    return {
        "message": "Veículo atualizado com sucesso!",
        "veiculo": veiculo
    }




@app.post("/manutencoes")
def cadastrar_manutencao(
    manutencao: ManutencaoCreate,
    banco: Session = Depends(obter_banco)
):

    # Verifica se o veículo existe
    veiculo = banco.query(Veiculo).filter(
        Veiculo.id == manutencao.veiculo_id
    ).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    # Converte a data recebida para Date
    data_manutencao = datetime.strptime(
        manutencao.data,
        "%Y-%m-%d"
    ).date()

    # Cria a nova manutenção
    nova_manutencao = Manutencao(
        veiculo_id=manutencao.veiculo_id,
        tipo=manutencao.tipo,
        data=data_manutencao,
        quilometragem=manutencao.quilometragem,
        descricao=manutencao.descricao,
        valor=manutencao.valor
    )

    banco.add(nova_manutencao)
    banco.commit()
    banco.refresh(nova_manutencao)

    # Identifica o tipo de manutenção
    tipo_manutencao = manutencao.tipo.lower()

    if "óleo" in tipo_manutencao or "oleo" in tipo_manutencao:
        veiculo.historico_oleo_conhecido = True

    elif "freio" in tipo_manutencao:
        veiculo.historico_freios_conhecido = True

    elif "bateria" in tipo_manutencao:
        veiculo.historico_bateria_conhecido = True

    elif "pneu" in tipo_manutencao:
        veiculo.historico_pneus_conhecido = True

    elif "filtro" in tipo_manutencao:
        veiculo.historico_filtros_conhecido = True

    elif "correia" in tipo_manutencao:
        veiculo.historico_correia_conhecido = True

    banco.commit()

    return {
        "message": "Manutenção cadastrada com sucesso!",
        "manutencao": {
            "id": nova_manutencao.id,
            "veiculo_id": nova_manutencao.veiculo_id,
            "tipo": nova_manutencao.tipo,
            "data": str(nova_manutencao.data),
            "quilometragem": nova_manutencao.quilometragem,
            "descricao": nova_manutencao.descricao,
            "valor": nova_manutencao.valor
        }
    }

@app.get("/veiculos/{veiculo_id}/manutencoes")
def listar_manutencoes(
    veiculo_id: int,
    banco: Session = Depends(obter_banco)
):
    # Verifica se o veículo existe
    veiculo = banco.query(Veiculo).filter(
        Veiculo.id == veiculo_id
    ).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    # Busca as manutenções do veículo
    manutencoes = banco.query(Manutencao).filter(
        Manutencao.veiculo_id == veiculo_id
    ).all()

    return manutencoes

@app.get("/veiculos/{veiculo_id}/resumo")
def resumo_veiculo(
    veiculo_id: int,
    banco: Session = Depends(obter_banco)
):
    # Busca o veículo
    veiculo = banco.query(Veiculo).filter(
        Veiculo.id == veiculo_id
    ).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    # Busca todas as manutenções do veículo
    manutencoes = banco.query(Manutencao).filter(
        Manutencao.veiculo_id == veiculo_id
    ).all()

    # Calcula o total gasto
    total_gasto = sum(
        manutencao.valor for manutencao in manutencoes
        if manutencao.valor is not None
    )

    # Última manutenção
    ultima_manutencao = None

    if manutencoes:
        ultima_manutencao = max(
            manutencoes,
            key=lambda manutencao: manutencao.data
        )

    return {
        "veiculo": {
            "id": veiculo.id,
            "marca": veiculo.marca,
            "modelo": veiculo.modelo,
            "ano": veiculo.ano,
            "quilometragem": veiculo.quilometragem,
            "combustivel": veiculo.combustivel
        },
        "resumo": {
            "quantidade_manutencoes": len(manutencoes),
            "total_gasto": total_gasto,
            "ultima_manutencao": {
                "tipo": ultima_manutencao.tipo,
                "data": str(ultima_manutencao.data),
                "quilometragem": ultima_manutencao.quilometragem,
                "valor": ultima_manutencao.valor
            } if ultima_manutencao else None
        }
    }

@app.put("/manutencoes/{id}")
def atualizar_manutencao(
    id: int,
    dados: ManutencaoCreate,
    banco: Session = Depends(obter_banco)
):
    # Busca a manutenção
    manutencao = banco.query(Manutencao).filter(
        Manutencao.id == id
    ).first()

    if manutencao is None:
        raise HTTPException(
            status_code=404,
            detail="Manutenção não encontrada"
        )

    # Verifica se o veículo informado existe
    veiculo = banco.query(Veiculo).filter(
        Veiculo.id == dados.veiculo_id
    ).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    # Converte a data
    data_manutencao = datetime.strptime(
        dados.data,
        "%Y-%m-%d"
    ).date()

    # Atualiza os dados
    manutencao.veiculo_id = dados.veiculo_id
    manutencao.tipo = dados.tipo
    manutencao.data = data_manutencao
    manutencao.quilometragem = dados.quilometragem
    manutencao.descricao = dados.descricao
    manutencao.valor = dados.valor

    banco.commit()
    banco.refresh(manutencao)

    return {
        "message": "Manutenção atualizada com sucesso!",
        "manutencao": {
            "id": manutencao.id,
            "veiculo_id": manutencao.veiculo_id,
            "tipo": manutencao.tipo,
            "data": str(manutencao.data),
            "quilometragem": manutencao.quilometragem,
            "descricao": manutencao.descricao,
            "valor": manutencao.valor
        }
    }

@app.delete("/manutencoes/{id}")
def excluir_manutencao(
    id: int,
    banco: Session = Depends(obter_banco)
):
    # Busca a manutenção
    manutencao = banco.query(Manutencao).filter(
        Manutencao.id == id
    ).first()

    # Verifica se ela existe
    if manutencao is None:
        raise HTTPException(
            status_code=404,
            detail="Manutenção não encontrada"
        )

    # Exclui a manutenção
    banco.delete(manutencao)
    banco.commit()

    return {
        "message": "Manutenção excluída com sucesso!"
    }

@app.get("/veiculos/{veiculo_id}/lembretes")
def verificar_lembretes(
    veiculo_id: int,
    banco: Session = Depends(obter_banco)
):

    # Busca o veículo
    veiculo = banco.query(Veiculo).filter(
        Veiculo.id == veiculo_id
    ).first()

    if veiculo is None:
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado"
        )

    # Busca as manutenções do veículo
    manutencoes = banco.query(Manutencao).filter(
        Manutencao.veiculo_id == veiculo_id
    ).all()

    lembretes = []

    # ==========================================
    # ÓLEO
    # ==========================================

    trocas_oleo = [
        manutencao
        for manutencao in manutencoes
        if "óleo" in manutencao.tipo.lower()
        or "oleo" in manutencao.tipo.lower()
    ]

    if not veiculo.historico_oleo_conhecido:

        lembretes.append({
            "tipo": "Troca de óleo",
            "status": "historico_desconhecido",
            "mensagem": "Não foi possível confirmar quando foi realizada a última troca de óleo.",
            "recomendacao": "Verifique o histórico do veículo ou considere realizar uma troca de óleo."
        })

    elif trocas_oleo:

        ultima_troca = max(
            trocas_oleo,
            key=lambda manutencao: manutencao.data
        )

        km_desde_troca = (
            veiculo.quilometragem
            - ultima_troca.quilometragem
        )

        dias_desde_troca = (
            datetime.now().date()
            - ultima_troca.data
        ).days

        limite_km = 10000
        limite_dias = 365

        km_restantes = limite_km - km_desde_troca
        dias_restantes = limite_dias - dias_desde_troca

        if (
            km_desde_troca >= limite_km
            or dias_desde_troca >= limite_dias
        ):
            status = "atrasada"
            mensagem = "A troca de óleo está atrasada."

        elif (
            km_restantes <= 1000
            or dias_restantes <= 30
        ):
            status = "proxima"
            mensagem = "A troca de óleo está próxima."

        else:
            status = "em_dia"
            mensagem = "A troca de óleo está em dia."

        lembretes.append({
            "tipo": "Troca de óleo",
            "status": status,
            "mensagem": mensagem,
            "ultima_troca": str(ultima_troca.data),
            "quilometragem_ultima_troca": ultima_troca.quilometragem,
            "quilometragem_atual": veiculo.quilometragem,
            "km_desde_troca": km_desde_troca,
            "km_restantes": max(km_restantes, 0),
            "dias_desde_troca": dias_desde_troca,
            "dias_restantes": max(dias_restantes, 0)
        })

    # ==========================================
    # FREIOS
    # ==========================================

    if not veiculo.historico_freios_conhecido:

        lembretes.append({
            "tipo": "Freios",
            "status": "historico_desconhecido",
            "mensagem": "Não foi possível confirmar a última manutenção dos freios.",
            "recomendacao": "Verifique o histórico ou solicite uma inspeção dos freios."
        })

    # ==========================================
    # BATERIA
    # ==========================================

    trocas_bateria = [
        manutencao
        for manutencao in manutencoes
        if "bateria" in manutencao.tipo.lower()
    ]

    if not veiculo.historico_bateria_conhecido:
                lembretes.append({
                    "tipo": "Bateria",
                    "status": "historico_desconhecido",
                    "mensagem": "Não foi possível confirmar a última troca da bateria.",
                    "recomendacao": "Verifique o histórico ou solicite uma avaliação da bateria."
                })

    elif trocas_bateria:

            ultima_bateria = max(
                trocas_bateria,
                key=lambda manutencao: manutencao.data
            )

            km_desde_troca = (
                veiculo.quilometragem
                - ultima_bateria.quilometragem
            )

            dias_desde_troca = (
                datetime.now().date()
                - ultima_bateria.data
            ).days

            limite_km = 50000
            limite_dias = 365 * 3

            km_restantes = limite_km - km_desde_troca
            dias_restantes = limite_dias - dias_desde_troca

            if (
                km_desde_troca >= limite_km
                or dias_desde_troca >= limite_dias
            ):
                status = "atrasada"
                mensagem = "A bateria pode estar próxima do fim da vida útil."

            elif (
                km_restantes <= 5000
                or dias_restantes <= 180
            ):
                status = "proxima"
                mensagem = "A bateria está próxima do período de avaliação recomendado."

            else:
                status = "em_dia"
                mensagem = "A bateria está dentro do período estimado de uso."

            lembretes.append({
                "tipo": "Bateria",
                "status": status,
                "mensagem": mensagem,
                "ultima_troca": str(ultima_bateria.data),
                "quilometragem_ultima_troca": ultima_bateria.quilometragem,
                "quilometragem_atual": veiculo.quilometragem,
                "km_desde_troca": km_desde_troca,
                "km_restantes": max(km_restantes, 0),
                "dias_desde_troca": dias_desde_troca,
                "dias_restantes": max(dias_restantes, 0)
            })

    # ==========================================
    # PNEUS
    # ==========================================

    if not veiculo.historico_pneus_conhecido:

        lembretes.append({
            "tipo": "Pneus",
            "status": "historico_desconhecido",
            "mensagem": "Não foi possível confirmar a última manutenção ou troca dos pneus.",
            "recomendacao": "Verifique o histórico e o estado atual dos pneus."
        })

    # ==========================================
    # FILTROS
    # ==========================================

    if not veiculo.historico_filtros_conhecido:

        lembretes.append({
            "tipo": "Filtros",
            "status": "historico_desconhecido",
            "mensagem": "Não foi possível confirmar a última troca dos filtros.",
            "recomendacao": "Verifique o histórico das trocas de filtros."
        })

    # ==========================================
    # CORREIA
    # ==========================================

    if not veiculo.historico_correia_conhecido:

        lembretes.append({
            "tipo": "Correia",
            "status": "historico_desconhecido",
            "mensagem": "Não foi possível confirmar a última manutenção da correia.",
            "recomendacao": "Verifique o histórico ou solicite uma inspeção."
        })

    # ==========================================
    # RESPOSTA
    # ==========================================

    return {
        "veiculo": {
            "id": veiculo.id,
            "marca": veiculo.marca,
            "modelo": veiculo.modelo,
            "ano": veiculo.ano,
            "quilometragem": veiculo.quilometragem
        },
        "lembretes": lembretes
    }