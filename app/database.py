import pathlib

from sqlmodel import Session, SQLModel, create_engine

p = pathlib.Path(__file__).parent / "roamy.db"

sqlite_url = f"sqlite:///{p}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def db_connect():
    SQLModel.metadata.create_all(engine)
