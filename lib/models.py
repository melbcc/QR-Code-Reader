import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Date

BaseModel = declarative_base()


class Member(BaseModel):
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

    @property
    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in (
                'id',
                'first_name', 'last_name', 'postal_code',
                'membshipnum', 'end_date', 'status_id', 'status_name',
            )
        }

#class Event(BaseModel):
#    __tablename__ = 'events'
#    id = Column(Integer, primary_key=True)
#    title = Column(String(250))
#
#class Attendance(BaseModel):
#    __tablename__ = 'attendance'
#    id = Column(Integer, primary_key=True)
#    member = ForeignKey(Member)
#    event = ForeignKey(Event)

class Location(BaseModel):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
