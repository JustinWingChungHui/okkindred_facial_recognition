from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from local_models import Base, Record
from resize_tags import resize_tags

import datetime
import os
import sys
import time


def check_resize_tags(now):

    print('Loading db data', flush=True)
    engine = create_engine('sqlite:///local.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    record = session.query(Record).filter(Record.name=="resize_tags last run date").one()
    print('Last run date: {}'.format(record.date_record), flush=True)

    resize_tags(record.date_record)
    record.date_record = now
    record.last_updated_date = datetime.datetime.now()

    print('Updating local db', flush=True)
    session.commit()



path = sys.path[0]
print('Monitoring {}'.format(path), flush=True)

while True:

    now = datetime.datetime.now()
    print('checking for flag(s) {}'.format(now), flush=True)

    resize_tags_flag = path + '/resize_tags.flag'
    if os.path.exists(resize_tags_flag):
        print('** Detected {} **'.format(resize_tags_flag), flush=True)

        check_resize_tags(now)

        print('Deleting flag', flush=True)
        os.remove(resize_tags_flag)

        print('')

    time.sleep(30)






