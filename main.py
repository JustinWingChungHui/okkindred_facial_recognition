import datetime
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Message, Queue
from secrets import DATABASE, MESSAGE_CHECK_INTERVAL_SECONDS, BATCH_SIZE
from resize_tag import resize_tags
from image_face_detect import image_face_detect
from profile_photo_process import profile_photo_process
from tag_converted_process import tag_converted_process
from person_deleted_update_face_model import person_deleted_update_face_model




print('Getting queue data')
print('')

print('Connecting to db')
# mysql+mysqldb://<user>:<password>@<host>/<dbname>
connection_string = 'mysql+mysqldb://{0}:{1}@{2}/{3}'.format(DATABASE['USER'],
                                                                DATABASE['PASSWORD'],
                                                                DATABASE['HOST'],
                                                                DATABASE['NAME'])

engine = create_engine(connection_string)
connection = engine.connect()
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()


# Getting queue ids for any queues that need processing
print('Getting queue data')
queues = session.query(Queue).all()

resize_tag_queue_id = next(q.id for q in queues if q.name == 'resize_tag')
image_face_detect_id = next(q.id for q in queues if q.name == 'image_face_detect')
profile_photo_process_id = next(q.id for q in queues if q.name == 'profile_photo_process')
tag_converted_process_id = next(q.id for q in queues if q.name == 'tag_converted_process')
person_deleted_update_face_model_id = next(q.id for q in queues if q.name == 'person_deleted_update_face_model')

# Close this connection
session.close()
engine.dispose()

print('resize_tag_queue_id: {}'.format(resize_tag_queue_id))

while True:

    # Get unprocessed messages
    print('{} Checking queue...'.format(datetime.datetime.now()))
    engine = create_engine(connection_string, pool_size=2, max_overflow=0)
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()

    print('Getting tag_resize messages')
    messages = session.query(Message). \
                    filter(Message.processed == False). \
                    filter(Message.error == False). \
                    order_by(Message.creation_date.asc()). \
                    limit(BATCH_SIZE).all()

    print('Total number of messages: {}'.format(len(messages)))

    # Split up messages to be handled NB filter does weird stuff with object references
    resize_messages = []
    image_face_detect_messages = []
    profile_photo_process_messages = []
    tag_converted_process_messages = []
    person_deleted_update_face_model_messages = []

    for message in messages:

        # resize_tag message
        if message.queue_id == resize_tag_queue_id:
            resize_messages.append(message)

        elif message.queue_id == image_face_detect_id:
            image_face_detect_messages.append(message)

        elif message.queue_id == profile_photo_process_id:
            profile_photo_process_messages.append(message)

        elif message.queue_id == tag_converted_process_id:
            tag_converted_process_messages.append(message)

        elif message.queue_id == person_deleted_update_face_model_id:
            person_deleted_update_face_model_messages.append(message)

    print('resize_messages: {}'.format(len(resize_messages)))
    print('image_face_detect_messages: {}'.format(len(image_face_detect_messages)))
    print('profile_photo_process_messages: {}'.format(len(profile_photo_process_messages)))
    print('tag_converted_process_messages: {}'.format(len(tag_converted_process_messages)))
    print('person_deleted_update_face_model_messages: {}'.format(len(person_deleted_update_face_model_messages)))

    # Process resize_tags messages
    if len(resize_messages) > 0:
        resize_tags(resize_messages, session)

    # Process face detect messages
    if len(image_face_detect_messages) > 0:
        image_face_detect(image_face_detect_messages, session)

    if len(profile_photo_process_messages) > 0:
        profile_photo_process(profile_photo_process_messages, session)

    if len(tag_converted_process_messages) > 0:
        tag_converted_process(tag_converted_process_messages, session)

    if len(person_deleted_update_face_model_messages) > 0:
        person_deleted_update_face_model(person_deleted_update_face_model_messages, session)

    # Close connection so we don't run out of connections
    session.close()
    engine.dispose()

    print('==== Finished Processing Messages ====')

    # Wait 5 seconds until next queue check
    time.sleep(MESSAGE_CHECK_INTERVAL_SECONDS)
    print('')





