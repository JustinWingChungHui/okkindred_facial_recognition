from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Queue(Base):
    __tablename__ = 'message_queue_queue'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), primary_key=True)


class Message(Base):
    __tablename__ = 'message_queue_message'
    id = Column(Integer, primary_key=True)
    queue_id = Column(Integer, ForeignKey('message_queue_queue.id'))
    processed = Column(Boolean, nullable=False)
    string_data = Column(String(250), nullable=True)
    integer_data = Column(Integer, nullable=True)
    float_data = Column(Float, nullable=True)
    date_data = Column(DateTime, nullable=True)
    creation_date = Column(DateTime, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)



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