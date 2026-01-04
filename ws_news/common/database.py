from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from contextlib import contextmanager
from typing import Generator
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    headline = Column(String, nullable=False)
    text = Column(Text)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Article(id={self.id}, headline='{self.headline}', source='{self.source}')>"


def get_engine() -> db.Engine:
    return db.create_engine("sqlite:///database.db")


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created successfully!")


@contextmanager
def get_connection():
    engine = get_engine()
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
