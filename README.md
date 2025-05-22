# Yüz Tanıma ile Giriş/Çıkış Takip Sistemi

Bu proje, yüz tanıma teknolojisi kullanarak çalışanların giriş ve çıkış saatlerini kaydeden bir Python uygulamasıdır. Webcam üzerinden gerçek zamanlı yüz tanıma yapılır ve bilgiler MySQL veritabanına yazılır.

## Özellikler

- Gerçek zamanlı yüz tanıma (face_recognition ve OpenCV)
- Tkinter ile kullanıcı arayüzü
- MySQL veritabanına giriş/çıkış kaydı
- Kişiye özel yüz tanıma (encoding karşılaştırması)

## Gereksinimler

- Python 3.x
- `face_recognition`
- `opencv-python`
- `numpy`
- `Pillow`
- `mysql-connector-python`
- `tkinter` (standart Python GUI modülü)

Kurulum:
```bash
pip install face_recognition opencv-python numpy Pillow mysql-connector-python
