"""
Resizes existing tags if using facial recognition
"""

from models import Base, Image, Tag
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secrets import DATABASE, MEDIA_ROOT
from file_downloader import download_file, get_file_name
import face_recognition

import os
import glob


def resize_tags(min_creation_date):
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

    db_images = dict()
    face_locations_by_image_id = dict()

    print('Get all tags')
    tags = session.query(Tag).filter(Tag.creation_date > min_creation_date).all()
    print('Total number of tags: {}'.format(len(tags)))

    match_tags = 0

    for tag in tags:
        print('')
        print('################################')
        print('tag.id = {}'.format(tag.id))
        tag_center = {
            'x': (tag.x2 + tag.x1) / 2,
            'y': (tag.y2 + tag.y1) / 2,
        }

        print('tag_center = {}'.format(tag_center))

        if tag.image_id in db_images:
            print('Using cached data')
            db_image = db_images[tag.image_id]
            local_file = get_file_name(db_image.large_thumbnail)
            print(db_image.title)
            print(local_file)

            locations = face_locations_by_image_id[tag.image_id]

        else:
            print('Getting image')
            db_image = session.query(Image).filter(Image.id == tag.image_id).one()
            db_images[tag.image_id] = db_image

            print('Downloading file')
            local_file = download_file(db_image.large_thumbnail)
            print(db_image.title)
            print(local_file)

            print('Loading the file into a numpy array')
            image = face_recognition.load_image_file(local_file)

            print('Finding faces')
            locations = face_recognition.face_locations(image)

            print('I found {} face(s) in this photograph.'.format(len(locations)))
            face_locations_by_image_id[tag.image_id] = locations


        for location in locations:
            top, right, bottom, left = location

            print('Normalized detected locations')
            x1 = left / db_image.large_thumbnail_width
            x2 = right / db_image.large_thumbnail_width
            y1 = top / db_image.large_thumbnail_height
            y2 = bottom / db_image.large_thumbnail_height

            print('x1:{0}, x2:{1}, y1:{2}, y2:{3}'.format(x1, x2, y1, y2))

            if x1 < tag_center['x'] and tag_center['x'] < x2:
                if y1 < tag_center['y'] and tag_center['y'] < y2:
                    print('8888888888888888888888888888 Match found!!!! 88888888888888888888888888888888888')
                    match_tags += 1

                    # Update tag with facial detection
                    print('Updating tag with new dimensions')
                    tag.x1 = x1
                    tag.x2 = x2
                    tag.y1 = y1
                    tag.y2 = y2



    print('')
    print('Matched: {}'.format(match_tags))
    if match_tags > 0:
        print('Updating database')
        session.commit()

    print('========DONE===========')












