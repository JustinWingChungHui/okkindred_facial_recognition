from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Image(Base):
    __tablename__ = 'gallery_image'
    id = Column(Integer, primary_key=True)
    large_thumbnail = Column(String(250), nullable=False)
    large_thumbnail_height = Column(Integer, nullable=False)
    large_thumbnail_width = Column(Integer, nullable=False)
    creation_date = Column(DateTime, nullable=False)