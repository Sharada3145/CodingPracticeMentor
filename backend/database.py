from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./mentor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema_updates():
    with engine.begin() as conn:
        table_rows = conn.exec_driver_sql("PRAGMA table_info(attempts)").fetchall()
        columns = {row[1] for row in table_rows}
        if "confidence" not in columns:
            conn.exec_driver_sql(
                "ALTER TABLE attempts ADD COLUMN confidence VARCHAR(20) DEFAULT 'medium'"
            )