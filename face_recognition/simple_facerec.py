import face_recognition
import cv2
import os
import glob
import numpy as np
 
#bu kod önceden yapılan kameradan alınan görüntünün kime ait olduğunu bulmak için kullanılıyor


class SimpleFacerec:
    def __init__(self):
        self.known_face_encodings = [] #tanınan yüzlerin vektörlere çevrilmiş halini saklar
        self.known_face_names = []     #tanınan yüzlerin isimlerini saklar
        self.frame_resizing = 0.25     

    def load_encoding_images(self, images_path):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        
        images_path = glob.glob(os.path.join(images_path, "*.*"))  #Görüntülerin yolu belirlenir ve klasördeki tüm resimler bulunur.

        print("{} encoding images found.".format(len(images_path)))

       
        for img_path in images_path:
            img = cv2.imread(img_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR formatını RGB'ye çevirir

           # Dosya adını alır
            basename = os.path.basename(img_path)
            (filename, ext) = os.path.splitext(basename)
           
            img_encoding = face_recognition.face_encodings(rgb_img)[0]  #Resimdeki yüz tanınarak encoding değeri çıkarılır:

           
            self.known_face_encodings.append(img_encoding)
            self.known_face_names.append(filename)
        print("Encoding images loaded")

    def detect_known_faces(self, frame): #yüz tanıma
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
       

        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        #Çerçevede yüzleri tespit etme işlemi yapılır
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        #Çerçevede yüzleri tespit etme işlemi yapılır:

        for face_encoding in face_encodings:
            
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        


        return face_locations.astype(int), face_names
