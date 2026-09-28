from database import engine, Base
from models import Veiculo

print("Criando tabelas...")

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")