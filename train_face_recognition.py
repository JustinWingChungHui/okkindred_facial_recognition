# https://github.com/ageitgey/face_recognition/blob/master/examples/face_recognition_knn.py

import math
import os
import pickle
from PIL import Image as PilImage
from sklearn import neighbors
from models import Person, Image, Tag, FaceModel
from secrets import TRAIN_FACE_RECOGNITION_TEMP_DIR
from file_downloader import download_file, clear_directory
import face_recognition


def get_file_for_tag(tag, image, session, dir_name):
    '''
    Gets file for tag and image
    '''
    print('        = Processing Tag and Image =')
    print('        tag.id: {}'.format(tag.id))
    print('        image.id: {}'.format(image.id))

    file = download_file(dir_name, image.large_thumbnail)

    print('        Opening Image')
    original = PilImage.open(file)

    print('        Cropping image')
    left = tag.x1 * image.large_thumbnail_width
    right = tag.x2 * image.large_thumbnail_width
    top = tag.y1 * image.large_thumbnail_height
    bottom = tag.y2 * image.large_thumbnail_height

    cropped = original.crop((left, top, right, bottom))
    cropped.save(file)

    return file



def process_person(person, session, X, y):
    '''
    Processes images for one person
    '''
    print('    == Processing person name: {0} id: {1} =='.format(person.name, person.id))
    dir_name = os.path.join(TRAIN_FACE_RECOGNITION_TEMP_DIR, str(person.id))

    print('    Creating directory {}'.format(dir_name))
    os.mkdir(dir_name)

    files = []

    if person.large_thumbnail:
        print('    Getting profile photo'.format(dir_name))
        files.append(download_file(dir_name, person.large_thumbnail))

    print('    Get all face detected tags for person')
    tags_and_images = session.query(Tag, Image). \
            filter(Tag.person_id == person.id). \
            filter(Tag.face_detected ==  True). \
            filter(Tag.image_id == Image.id).all()

    print('    Total number of tags: {}'.format(len(tags_and_images)))

    for tag, image in tags_and_images:
        files.append(get_file_for_tag(tag, image, session, dir_name))

    print('    Process Images')
    for file in files:
        process_file(file, X, y, person.id)


def process_file(file, X, y, person_id):
    print('        Creating face encoding for {}'.format(file))
    im = face_recognition.load_image_file(file)
    face_bounding_boxes = face_recognition.face_locations(im)

    # Add face encoding for current image to the training set
    if len(face_bounding_boxes) == 1:
        print('        Adding face to model')
        X.append(face_recognition.face_encodings(im, known_face_locations=face_bounding_boxes)[0])
        y.append(person_id)
    else:
        print('        XXX No Face Found!!! XXX')


def process_family(family_id, session):
    '''
    Creates a K Nearest neighbour model for a family
    '''
    print('')
    print('===== Processing Family_id: {} ====='.format(family_id))
    print('Clearing working directory')
    clear_directory(TRAIN_FACE_RECOGNITION_TEMP_DIR)

    face_model = FaceModel(family_id = family_id)

    print('Get all people for family')
    people = session.query(Person).filter(Person.family_id == family_id).all()
    print('Total number of people: {}'.format(len(people)))


    X = []
    y = []


    for person in people:
        process_person(person, session, X, y)

    if (len(X) > 0):
        n_neighbors = int(round(math.sqrt(len(X))))
        print('Setting n_neighbors to {}'.format(n_neighbors))

        print('Creating and training the KNN classifier')
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm='ball_tree', weights='distance')
        knn_clf.fit(X, y)

        print('y:')
        print(y)

        print('Pickling and saving to db')
        face_model.fit_data_faces = pickle.dumps(X)
        face_model.fit_data_person_ids = pickle.dumps(y)
        face_model.n_neighbors = n_neighbors
        face_model.trained_knn_model = pickle.dumps(knn_clf)

        session.add(face_model)
        session.commit()

    else:
        print('Not enough data to create model')



#print('#############################################')
#print('')

#print('Connecting to db')
# mysql+mysqldb://<user>:<password>@<host>/<dbname>
#connection_string = 'mysql+mysqldb://{0}:{1}@{2}/{3}'.format(DATABASE['USER'],
#                                                                DATABASE['PASSWORD'],
#                                                                DATABASE['HOST'],
#                                                                DATABASE['NAME'])
#engine = create_engine(connection_string)
#Base.metadata.bind = engine
#DBSession = sessionmaker()
#DBSession.bind = engine
#session = DBSession()

#print('Get all families')
#families = session.query(Family).all()
#print('Total number of families: {}'.format(len(families)))

#for family in  families:
#    process_family(family.id, session)


