from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Record(Base):
    __tablename__ = 'records'
    name = Column(String(100), primary_key=True)
    description = Column(String(250), nullable=False)
    string_record = Column(String(250), nullable=True)
    integer_record = Column(Integer, nullable=True)
    float_record = Column(Float, nullable=True)
    date_record = Column(DateTime, nullable=True)
    last_updated_date = Column(DateTime, nullable=False)
