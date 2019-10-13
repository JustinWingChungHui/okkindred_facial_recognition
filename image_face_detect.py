import datetime
import pickle
from models import Image, SuggestedTag, FaceModel, Person
from secrets import IMAGE_FACE_DETECT_TEMP_DIR
from file_downloader import download_file, clear_directory
import face_recognition

def image_face_detect(messages, session):

    try:
        clear_directory(IMAGE_FACE_DETECT_TEMP_DIR)

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

        face_models = {}

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

                print('Loading Face model for family')
                if db_image.family_id in face_models:
                    face_model = face_models[db_image.family_id]
                else:
                    face_model = session.query(FaceModel).filter(FaceModel.family_id == db_image.family_id).first()
                    face_models[db_image.family_id] = face_model

                if face_model:
                    print('Matching face')

                    print('Loading Training Model')
                    trained_knn_model = pickle.loads(face_model.trained_knn_model)

                    print('Find encodings for faces in the image')
                    faces_encodings = face_recognition.face_encodings(image, known_face_locations=(location,))

                    distances, fit_face_indexes = trained_knn_model.kneighbors(faces_encodings, n_neighbors=1)

                    print('distances:')
                    print(distances)
                    print('fit_face_indexes:')
                    print(fit_face_indexes)

                    if len(distances) > 0 and len(distances[0]) > 0:
                        fit_data_person_ids = pickle.loads(face_model.fit_data_person_ids)

                        if len(fit_data_person_ids) > fit_face_indexes[0][0]:

                            # Check person exists
                            person_id = fit_data_person_ids[fit_face_indexes[0][0]]
                            if session.query(Person).filter(Person.id == person_id).first():

                                print('Adding matched person')
                                new_suggested_tag.probability = distances[0][0]
                                new_suggested_tag.person_id = person_id

                            else:
                                print('Invalid person_id: {}'.format(person_id))

                session.add(new_suggested_tag)

                suggested_tag_count += 1


        print('')
        print('Suggested tags created: {}'.format(suggested_tag_count))
        # Messages processed
        for message in messages:
            message.processed = True

    except Exception as e:
        print(e)

        for message in messages:
            message.error = True
            message.error_message = str(e)[:512]

    session.commit()

    print('========DONE===========')



