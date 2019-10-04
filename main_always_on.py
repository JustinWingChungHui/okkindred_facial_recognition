from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Message, Queue

from secrets import DATABASE
from resize_tag import resize_tags
import datetime
import time



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
engine.dispose()

# Getting queue ids for any queues that need processing
print('Getting queue data')
queues = session.query(Queue).all()

resize_tag_queue_id = next(q.id for q in queues if q.name == 'resize_tag')

session.close()



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
                    filter(Message.processed == False).all()

    print('Number of messages: {}'.format(len(messages)))

    # Process resize_tags messages
    resize_messages = filter(lambda m: m.queue_id == resize_tag_queue_id , messages)
    resize_tags(resize_messages, session)

    # Messages processed
    for message in messages:
        message.processed = True

    session.commit()

    # Close connection so we don't run out of connections
    session.close()
    engine.dispose()

    # Wait 5 seconds until next queue check
    time.sleep(5)






