from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Image(Base):
    __tablename__ = 'gallery_image'
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    large_thumbnail = Column(String(250), nullable=False)
    large_thumbnail_height = Column(Integer, nullable=False)
    large_thumbnail_width = Column(Integer, nullable=False)
    creation_date = Column(DateTime, nullable=False)


class Tag(Base):
    __tablename__ = 'gallery_tag'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('gallery_image.id'))
    person_id = Column(Integer, nullable=False)
    x1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, nullable=False)