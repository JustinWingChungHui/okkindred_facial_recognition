import math
import pickle
from sklearn import neighbors
from models import Image, Tag, FaceModel
from secrets import TRAIN_FACE_RECOGNITION_TEMP_DIR
from file_downloader import clear_directory
from train_face_recognition import process_family, process_file, get_file_for_tag

def tag_converted_process(messages, session):
    try:
        tag_ids = []

        for message in messages:
            print('message.integer_data: {}'.format(message.integer_data))
            if message.integer_data:
                tag_ids.append(message.integer_data)

        print('Get people {}'.format(tag_ids))
        print('    Get all face detected tags for person')
        tags_and_images = session.query(Tag, Image). \
                filter(Tag.id.in_(tag_ids)). \
                filter(Tag.image_id == Image.id).all()

        print('Group into families')
        families = {}
        for tag, image in tags_and_images:
            if not image.family_id in families:
                families[image.family_id] = []

            families[image.family_id].append((tag, image))

        print(families)

        for family_id in families.keys():
            update_family_model(family_id, families[family_id], session)

        for message in messages:
            message.processed = True

    except Exception as e:
        print(e)

        for message in messages:
            message.error = True
            message.error_message = str(e)

    session.commit()


def update_family_model(family_id, tags_and_images, session):
    print('update_family_model() family_id: {}'.format(family_id))
    clear_directory(TRAIN_FACE_RECOGNITION_TEMP_DIR)

    print('Getting Face Models for family')
    face_model = session.query(FaceModel).filter(family_id == family_id).first()

    if not face_model:
        print('No face model, create new one')
        process_family(family_id, session)

    else:
        X = pickle.loads(face_model.fit_data_faces)
        y = pickle.loads(face_model.fit_data_person_ids)

        files = []
        for tag, image in tags_and_images:
            if image.large_thumbnail:
                file = get_file_for_tag(tag, image, session, TRAIN_FACE_RECOGNITION_TEMP_DIR)
                files.append(file)

                process_file(file, X, y, tag.person_id)

        if len(files) > 0:
            n_neighbors = int(round(math.sqrt(len(X))))
            print('Setting n_neighbors to {}'.format(n_neighbors))

            print('Creating and training the KNN classifier')
            knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm='ball_tree', weights='distance')
            knn_clf.fit(X, y)

            print('Pickling and saving to db')
            face_model.fit_data_faces = pickle.dumps(X)
            face_model.fit_data_person_ids = pickle.dumps(y)
            face_model.n_neighbors = n_neighbors
            face_model.trained_knn_model = pickle.dumps(knn_clf)
