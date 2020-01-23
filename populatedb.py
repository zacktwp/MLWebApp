from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Polution, Base, User
import datetime

datetime_object = datetime.datetime.now()

engine = create_engine('sqlite:///polution.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(name="zack peterson", email="zacktwp@gmail.com")

session.add(user1)
session.commit()

Polution1 = Polution(created_date=datetime_object,
                    name="first",
                    polution="0",
                    dew="0",
                    temp="0",
                    pres="0",
                    wnddir="0",
                    wndspd="0",
                    snow="0",
                    rain="0")

session.add(Polution1)
session.commit()

print ("added Polution to DB!")
