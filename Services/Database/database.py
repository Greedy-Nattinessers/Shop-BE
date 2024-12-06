from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from Services.Config.config import config

engine = create_engine(
    f"mysql://{config.database.username}:{config.database.password}@{config.database.host}:{config.database.port}/{config.database.name}",
    connect_args={"connect_timeout": 10},
)


SessionLocal = sessionmaker(autocommit=False, bind=engine, expire_on_commit=True)
Base = declarative_base()


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
