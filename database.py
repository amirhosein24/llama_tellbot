
from creds import home

from datetime import datetime

from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, Column, Integer, String, DateTime

engine = create_engine(f"sqlite:///{home}db.sqlite", poolclass=QueuePool,
                       pool_recycle=1800, connect_args={'check_same_thread': False})

Base = declarative_base()


class UserData(Base):
    __tablename__ = 'llama'

    user_id = Column(Integer, primary_key=True,
                     autoincrement=True, unique=True)
    chat_id = Column(Integer, unique=True)
    username = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    timejoined = Column(DateTime)
    total_usage = Column(Integer, default=0)
    limiter = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)  # Create tables if not exist


# function to add user
def add_user(chat_id, username, firstname, lastname, timejoined=datetime.now()):
    session = sessionmaker(bind=engine)()

    try:
        new_user = UserData(
            chat_id=chat_id,
            username=username,
            firstname=firstname,
            lastname=lastname,
            timejoined=timejoined)
        session.add(new_user)
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()
