from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from Services.Config.config import config

auth = f"{config.db_user}:{config.db_password}@"

engine = create_engine(
    f"mysql://{auth}{config.db_url}/{config.db_name}",
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
