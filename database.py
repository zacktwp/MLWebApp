import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Polution(Base):
    __tablename__ = 'polution'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    polution = Column(String(8))
    dew = Column(String(8))
    temp = Column(String(8))
    pres = Column(String(8))
    wnddir = Column(String(8))
    wndspd = Column(String(8))
    snow = Column(String(8))
    rain = Column(String(8))



engine = create_engine('sqlite:///polution.db')


Base.metadata.create_all(engine)
