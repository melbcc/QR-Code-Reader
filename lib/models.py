import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Date

Base = declarative_base()


class Member(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True)

    # Personal Data
    first_name = Column(String(250))
    last_name = Column(String(250))
    postal_code = Column(String(10))

    # Membership & Status
    membshipnum = Column(String(250))
    end_date = Column(Date())
    status_id = Column(String(250))
    status_name = Column(String(250))
