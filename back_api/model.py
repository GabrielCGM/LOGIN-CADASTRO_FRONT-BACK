from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def retorno_engine():
    USUARIO = ''
    SENHA = ''
    HOST = 'localhost'
    BANCO = 'loginapi'
    PORT = 3306

    conn = f'mysql+pymysql://{USUARIO}:{SENHA}@{HOST}:{PORT}/{BANCO}'
    engine = create_engine(conn, echo=False)
    return engine

def conect_banco():
    Session = sessionmaker(bind=retorno_engine())
    return Session()

class Info(Base):
    __tablename__ = 'Cadastro'
    id = Column(Integer, primary_key=True)
    nome = Column(String(20))
    email = Column(String(30))
    celular = Column(String(30))
    senha = Column(String(100))

Base.metadata.create_all(retorno_engine())
