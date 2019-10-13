from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, LargeBinary
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
    string_data = Column(String(512), nullable=True)
    integer_data = Column(Integer, nullable=True)
    float_data = Column(Float, nullable=True)
    date_data = Column(DateTime, nullable=True)
    error = Column(Boolean, nullable=False)
    error_message = Column(String(512), nullable=True)
    creation_date = Column(DateTime, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)



class Image(Base):
    __tablename__ = 'gallery_image'
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey('family_tree_family.id'), primary_key=True)
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
    face_detected = Column(Boolean, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, nullable=False)


class SuggestedTag(Base):
    __tablename__ = 'suggested_image_tagging_suggestedtag'
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('gallery_image.id'))
    person_id = Column(Integer, nullable=True)
    probability = Column(Float, nullable=True)
    x1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)
    last_updated_date = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, nullable=False)


class Family(Base):
    __tablename__ = 'family_tree_family'
    id = Column(Integer, primary_key=True)


class Person(Base):
    __tablename__ = 'family_tree_person'
    id = Column(Integer, primary_key=True)
    family_id = Column(Integer, ForeignKey('family_tree_family.id'))
    name = Column(String(250), nullable=False)
    large_thumbnail = Column(String(250), nullable=True)


class FaceModel(Base):
    __tablename__ = 'facial_recognition_facemodel'
    family_id = Column(Integer, ForeignKey('family_tree_family.id'), primary_key=True)
    fit_data_faces = Column(LargeBinary, nullable=False)
    fit_data_person_ids = Column(LargeBinary, nullable=False)
    n_neighbors = Column(Integer, nullable=False)
    trained_knn_model = Column(LargeBinary, nullable=False)



