import math
import pickle
from sklearn import neighbors
from models import Person, FaceModel
from secrets import TRAIN_FACE_RECOGNITION_TEMP_DIR
from file_downloader import download_file, clear_directory
from train_face_recognition import process_family, process_file

def profile_photo_process(messages, session):

    try:
        person_ids = []

        for message in messages:
            print('message.integer_data: {}'.format(message.integer_data))
            if message.integer_data:
                person_ids.append(message.integer_data)

        print('Get people {}'.format(person_ids))
        people = session.query(Person). \
            filter(Person.id.in_(person_ids)).all()

        print('Group into families')
        families = {}
        for person in people:
            if not person.family_id in families:
                families[person.family_id] = []

            families[person.family_id].append(person)

        print(families)

        for family_id in families.keys():
            update_family_model(family_id, families[family_id], session)

        for message in messages:
            message.processed = True

    except Exception as e:
        print(e)

        for message in messages:
            message.error = True
            message.error_message = str(e)[:512]

    session.commit()


def update_family_model(family_id, people, session):
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
        for person in people:
            if person.large_thumbnail:
                file = download_file(TRAIN_FACE_RECOGNITION_TEMP_DIR, person.large_thumbnail)
                files.append(file)

                process_file(file, X, y, person.id)

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






