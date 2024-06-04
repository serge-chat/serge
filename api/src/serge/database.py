from serge.models.settings import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = Settings()

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
