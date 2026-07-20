import face_recognition
import cv2
import numpy

TARGET_WIDTH = 500
NUM_UPSAMPLINGS = 1
MATCH_THRESHOLD = 0.65   # Maximum Euclidean distance to accept a match

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None, "Could not load image"
    height, width = image.shape[:2]
    scale = TARGET_WIDTH / width
    resized = cv2.resize(image, (TARGET_WIDTH, int(height * scale)))
    rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    return rgb_image, None

def select_largest_face(face_locations):
    largest = None
    max_area = 0
    for face in face_locations:
        top, right, bottom, left = face
        area = (bottom - top) * (right - left)
        if area > max_area:
            max_area = area
            largest = face
    return largest

def detect_face_locations(rgb_image):
    face_locations = face_recognition.face_locations(rgb_image, NUM_UPSAMPLINGS, model="hog")
    if len(face_locations) == 0:
        return None, "No face detected in image"
    if len(face_locations) > 1:
        face_locations = [select_largest_face(face_locations)]
    return face_locations, None

def extract_face_encoding(rgb_image, face_locations):
    """Generate a 128-dimension numerical encoding vector for the detected face."""
    encodings = face_recognition.face_encodings(rgb_image, face_locations)
    if len(encodings) == 0:
        return None, "Feature extraction failed"
    return encodings[0], None

def find_best_match(input_encoding, actors):
    """
    Compare input encoding against all stored actors using Euclidean distance.
    Returns (actor_dict, confidence) or (None, None) if no match found.
    """
    best_actor = None
    min_distance = float("inf")

    for actor in actors:
        distance = numpy.linalg.norm(input_encoding - actor["encoding"])  # Euclidean distance
        if distance < min_distance:
            min_distance = distance
            best_actor = actor

    if min_distance > MATCH_THRESHOLD:
        return None, None  # No match within threshold

    confidence = round((1 - min_distance) * 100, 1)
    return best_actor, confidence