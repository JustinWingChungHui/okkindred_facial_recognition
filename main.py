from models.image import Base, Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secrets import DATABASE, MEDIA_ROOT
from file_downloader import download_file

import os
import glob

print('#############################################')
print('')

print('Clearing working directory')
files = glob.glob('{0}*'.format(MEDIA_ROOT))
for f in files:
    os.remove(f)

print('Connecting to db')
# mysql+mysqldb://<user>:<password>@<host>/<dbname>
connection_string = 'mysql+mysqldb://{0}:{1}@{2}/{3}'.format(DATABASE['USER'],
                                                                DATABASE['PASSWORD'],
                                                                DATABASE['HOST'],
                                                                DATABASE['NAME'])

engine = create_engine(connection_string)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

print('Getting first image')
dbimage = session.query(Image).filter(Image.id == 133).one()

print(dbimage.large_thumbnail)


print('Downloading first image')
local_file = download_file(dbimage.large_thumbnail)

# OpenCV
# from opencv import detect_faces
# detect_faces(local_file)

from face_recog import detect_faces
detect_faces(local_file)



