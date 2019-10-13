import math
import json
import pickle
from sklearn import neighbors
from models import FaceModel
from train_face_recognition import process_family

def person_deleted_update_face_model(messages, session):
    try:
        people = []

        for message in messages:
            print('message.string_data: {}'.format(message.string_data))
            if message.string_data:
                person = json.loads(message.string_data)
                people.append(person)

        print('Group into families')
        families = {}
        for person in people:
            family_id = person['family_id']
            if not family_id in families:
                families[family_id] = []

            families[family_id].append(person)

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

    print('Getting Face Models for family')
    face_model = session.query(FaceModel).filter(family_id == family_id).first()

    if not face_model:
        print('No face model, create new one')
        process_family(family_id, session)

    else:
        X = pickle.loads(face_model.fit_data_faces)
        y = pickle.loads(face_model.fit_data_person_ids)

        index_removed = False

        print('Removing people from face models')
        for person in people:
            person_id = int(person['person_id'])
            while person_id in y:
                index = y.index(person_id)
                print('Removing index: {}'.format(index))
                y.pop(index)
                X.pop(index)
                index_removed = True

        if index_removed:
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



