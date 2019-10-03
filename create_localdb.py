from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from local_models import Base, Record
import datetime

print('####################################')
print('Creating db')
engine = create_engine('sqlite:///local.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

print('Creating resize_tags record')
new_record = Record(name = 'resize_tags last run date',
                    description = """Last date resize_tags was run.
                    Used to look at new tags and use facial recognition to make tag boundaries
                    better sized around faces
                    """,
                    date_record = datetime.datetime(2000, 1, 1),
                    last_updated_date = datetime.datetime.now())


session.add(new_record)
session.commit()

