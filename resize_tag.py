from models import Image, Tag
from secrets import RESIZE_TAG_TEMP_DIR
from file_downloader import download_file, get_file_name, clear_directory
import face_recognition


def resize_tags(messages, session):

    try:
        clear_directory(RESIZE_TAG_TEMP_DIR)

        db_images = dict()
        face_locations_by_image_id = dict()

        tag_ids = []
        for message in messages:
            if message.integer_data:
                tag_ids.append(message.integer_data)

        print('Get all tags')
        tags = session.query(Tag). \
                filter(Tag.id.in_(tag_ids)).all()

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
                local_file = get_file_name(RESIZE_TAG_TEMP_DIR, db_image.large_thumbnail)
                print(db_image.title)
                print(local_file)

                locations = face_locations_by_image_id[tag.image_id]

            else:
                print('Getting image')
                db_image = session.query(Image).filter(Image.id == tag.image_id).one()
                db_images[tag.image_id] = db_image

                print('Downloading file')
                local_file = download_file(RESIZE_TAG_TEMP_DIR, db_image.large_thumbnail)
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
                        tag.face_detected = True



        print('')
        print('Matched: {}'.format(match_tags))
        # Messages processed
        for message in messages:
            message.processed = True

    except Exception as e:
        print(e)
        for message in messages:
            message.error = True
            message.error_message = str(e)

    session.commit()

    print('========DONE===========')
