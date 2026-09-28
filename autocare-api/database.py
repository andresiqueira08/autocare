from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:Andregilson08!@localhost:5432/autocare"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def testar_conexao():
    try:
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        print("Conexão com PostgreSQL realizada com sucesso!")

    except Exception as erro:
        print("Erro ao conectar com PostgreSQL:")
        print(erro)


if __name__ == "__main__":
    testar_conexao()