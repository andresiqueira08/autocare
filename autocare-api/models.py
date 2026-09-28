from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False)
    quilometragem = Column(Integer, nullable=False)
    combustivel = Column(String(30), nullable=False)

    historico_desconhecido = Column(
        Boolean,
        nullable=False,
        default=True
    )

    historico_oleo_conhecido = Column(
        Boolean,
        nullable=False,
        default=False
    )
    historico_freios_conhecido = Column(
    Boolean,
    nullable=False,
    default=False
    )

    historico_bateria_conhecido = Column(
        Boolean,
        nullable=False,
        default=False
    )

    historico_pneus_conhecido = Column(
        Boolean,
        nullable=False,
        default=False
    )

    historico_filtros_conhecido = Column(
        Boolean,
        nullable=False,
        default=False
    )

    historico_correia_conhecido = Column(
        Boolean,
        nullable=False,
        default=False
    )

class Manutencao(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)

    veiculo_id = Column(
        Integer,
        ForeignKey("veiculos.id"),
        nullable=False
    )

    tipo = Column(String(100), nullable=False)
    data = Column(Date, nullable=False)
    quilometragem = Column(Integer, nullable=False)
    descricao = Column(String(500), nullable=True)
    valor = Column(Float, nullable=False)