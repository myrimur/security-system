
import face_recognition
import pickle

def get_encodings():
    # Load a sample picture and learn how to recognize it.
    obama_image = face_recognition.load_image_file("karyna.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image, model="large", num_jitters=100)[0]

    # Load a second sample picture and learn how to recognize it.
    biden_image = face_recognition.load_image_file("photo_2023-02-22_21-33-46.jpg")
    biden_face_encoding = face_recognition.face_encodings(biden_image, model="large", num_jitters=100)[0]

    volod = face_recognition.load_image_file("volodia.jpg")
    volod_encoding = face_recognition.face_encodings(volod, model="large", num_jitters=100)[0]

    svit = face_recognition.load_image_file("svitlana.jpg")
    svit_encoding = face_recognition.face_encodings(svit, model="large", num_jitters=100)[0]
    

    names = {
        "Karyna Volokhatiuk":obama_face_encoding,
        "Daria Minieieva":biden_face_encoding,
        "Volodymyr Kuzma":volod_encoding,
        "Svitlana Hovorova":svit_encoding
    }

    with open("temp_database.csv", "wb") as data:
        pickle.dump(names, data)
get_encodings()