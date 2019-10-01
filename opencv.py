import cv2
from secrets import MEDIA_ROOT

def detect_faces(local_file):
    print('Creating the front face haar cascade')
    cascPath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)

    print('Reading image')
    image = cv2.imread(local_file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    print('Detecting faces')
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    print('Drawing rectangles around faces')
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

    print('Creating the profile haar cascade')
    profileCascPath = "haarcascade_profileface.xml"
    profileCascade = cv2.CascadeClassifier(profileCascPath)

    print('Detecting profiles')
    profiles = profileCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )

    print('Drawing rectangles around profiles')
    for (x, y, w, h) in profiles:
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)


    print('Writing output image')
    cv2.imwrite('{0}output.jpg'.format(MEDIA_ROOT),image)