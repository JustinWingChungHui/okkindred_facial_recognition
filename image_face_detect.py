import datetime
from models import Image, SuggestedTag
from secrets import IMAGE_FACE_DETECT_TEMP_DIR
from file_downloader import download_file
import face_recognition

def image_face_detect(messages, session):

    import os
    import glob

    print('Clearing working directory')
    files = glob.glob('{0}*'.format(IMAGE_FACE_DETECT_TEMP_DIR))
    for f in files:
        os.remove(f)

    image_ids = []
    for message in messages:
        print('message.integer_data: {}'.format(message.integer_data))
        if message.integer_data:
            image_ids.append(message.integer_data)

    print('Get images {}'.format(image_ids))
    db_images = session.query(Image). \
            filter(Image.id.in_(image_ids)).all()

    print('Total number of images: {}'.format(len(db_images)))

    suggested_tag_count = 0

    for db_image in db_images:
        print('Downloading file')
        local_file = download_file(IMAGE_FACE_DETECT_TEMP_DIR, db_image.large_thumbnail)
        print(db_image.title)
        print(local_file)

        print('Loading the file into a numpy array')
        image = face_recognition.load_image_file(local_file)

        print('Finding faces')
        locations = face_recognition.face_locations(image)

        print('I found {} face(s) in this photograph.'.format(len(locations)))

        for location in locations:
            top, right, bottom, left = location

            print('Normalized detected locations')
            x1 = left / db_image.large_thumbnail_width
            x2 = right / db_image.large_thumbnail_width
            y1 = top / db_image.large_thumbnail_height
            y2 = bottom / db_image.large_thumbnail_height

            print('Creating suggested tag')
            new_suggested_tag = SuggestedTag(image_id = db_image.id,
                                                x1 = x1,
                                                x2 = x2,
                                                y1 = y1,
                                                y2 = y2,
                                                last_updated_date = datetime.datetime.utcnow(),
                                                creation_date = datetime.datetime.utcnow())

            session.add(new_suggested_tag)

            suggested_tag_count += 1


    print('')
    print('Suggested tags created: {}'.format(suggested_tag_count))
    # Messages processed
    for message in messages:
        message.processed = True

    session.commit()

    print('========DONE===========')


