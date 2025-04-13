import face_recognition
import cv2
import numpy as np
import mysql.connector
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import threading


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="son"
)
cursor = conn.cursor()


yuz_encodingleri = []
isimler = []
personel_idler = []

def yuz_encodingleri_yukle():
    cursor.execute("SELECT id, ad, soyad, yuz_dosya_yolu FROM EMPLOYEE")
    calisanlar = cursor.fetchall()

    for calisan in calisanlar:
        calisan_id, ad, soyad, yuz_dosya_yolu = calisan
        if yuz_dosya_yolu and os.path.exists(yuz_dosya_yolu):
            resim = face_recognition.load_image_file(yuz_dosya_yolu)
            encoding = face_recognition.face_encodings(resim)
            if encoding:
                yuz_encodingleri.append(encoding[0])
                isimler.append(f"{ad} {soyad}")
                personel_idler.append(calisan_id)


yuz_encodingleri_yukle()

video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)

root = tk.Tk()
root.title("Giriş/Çıkış Sistemi")

label = tk.Label(root)
label.pack()

def kamera_guncelle():
    """Kamera görüntüsünü sürekli günceller (Thread kullanmadan)."""
    ret, frame = video.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (320, 240))  
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    root.after(30, kamera_guncelle)  

def giris_yap():
    ret, frame = video.read()
    if not ret:
        messagebox.showerror("Hata", "Kameradan görüntü alınamadı!")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

    yuz_konumlari = face_recognition.face_locations(rgb_frame)
    
    if not yuz_konumlari:
        messagebox.showerror("Hata", "Yüz algılanamadı! Lütfen kameraya düzgün bakın.")
        return
        
    yuz_kodlari = face_recognition.face_encodings(rgb_frame, yuz_konumlari)

    for yuz_kodu in yuz_kodlari:
        eslesme_sonuclari = face_recognition.compare_faces(yuz_encodingleri, yuz_kodu)
        mesafeler = face_recognition.face_distance(yuz_encodingleri, yuz_kodu)
        en_iyi_eslesme = np.argmin(mesafeler)

        if eslesme_sonuclari[en_iyi_eslesme]:
            isim = isimler[en_iyi_eslesme]
            personel_id = personel_idler[en_iyi_eslesme]
            saat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO giris_cikis_kaydi (employee_id, giris_saati) VALUES (%s, %s)",
                           (personel_id, saat))
            conn.commit()
            messagebox.showinfo("Başarı", f"{isim} giriş yaptı! Saat: {saat}")
            return
    
    messagebox.showerror("Hata", "Tanınan bir yüz bulunamadı!")

def cikis_yap():
    ret, frame = video.read()
    if not ret:
        messagebox.showerror("Hata", "Kameradan görüntü alınamadı!")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)

    yuz_konumlari = face_recognition.face_locations(rgb_frame)
    
    if not yuz_konumlari:
        messagebox.showerror("Hata", "Yüz algılanamadı! Lütfen kameraya düzgün bakın.")
        return
        
    yuz_kodlari = face_recognition.face_encodings(rgb_frame, yuz_konumlari)

    for yuz_kodu in yuz_kodlari:
        eslesme_sonuclari = face_recognition.compare_faces(yuz_encodingleri, yuz_kodu)
        mesafeler = face_recognition.face_distance(yuz_encodingleri, yuz_kodu)
        en_iyi_eslesme = np.argmin(mesafeler)

        if eslesme_sonuclari[en_iyi_eslesme]:
            isim = isimler[en_iyi_eslesme]
            personel_id = personel_idler[en_iyi_eslesme]
            saat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            
            cursor.execute("""
                SELECT id FROM giris_cikis_kaydi
                WHERE employee_id = %s AND cikis_saati IS NULL
                ORDER BY giris_saati DESC LIMIT 1
            """, (personel_id,))
            sonuc = cursor.fetchone()

            if sonuc:
                kayit_id = sonuc[0]
                cursor.execute("UPDATE giris_cikis_kaydi SET cikis_saati = %s WHERE id = %s", (saat, kayit_id))
                conn.commit()
                messagebox.showinfo("Başarı", f"{isim} çıkış yaptı! Saat: {saat}")
            else:
                messagebox.showwarning("Uyarı", f"{isim} için açık giriş kaydı bulunamadı.")
            return
    
    messagebox.showerror("Hata", "Tanınan bir yüz bulunamadı!")


giris_button = tk.Button(root, text="Giriş Yap", command=giris_yap, width=20)
giris_button.pack(pady=10)

cikis_button = tk.Button(root, text="Çıkış Yap", command=cikis_yap, width=20)
cikis_button.pack(pady=10)


kamera_guncelle()

root.mainloop()

video.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()