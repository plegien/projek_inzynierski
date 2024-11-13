import numpy as np
import cv2
from picamera2 import Picamera2
from PIL import Image

# Funkcja do obliczania limitów HSV dla zielonego koloru (podejście dopasowane do Sprite)
def get_green_limits():
    # Precyzyjne wartości dla zielonej puszki Sprite
    lowerGreen = np.array([35, 130, 100], dtype=np.uint8)  # Zawężony zakres dla zieleni
    upperGreen = np.array([75, 255, 255], dtype=np.uint8)  # Węższy zakres
    return lowerGreen, upperGreen

# Funkcja do obliczania limitów HSV dla czerwonego koloru (Coca-Cola) - zmniejszenie zakresu
def get_red_limits():
    # Czerwony kolor w przestrzeni HSV (od prawdziwego czerwonego do intensywnego czerwonego)
    lowerRed = np.array([170, 120, 100], dtype=np.uint8)  # Granice dolne czerwonego
    upperRed = np.array([180, 255, 255], dtype=np.uint8)  # Granice górne czerwonego
    return lowerRed, upperRed

# Inicjalizacja kamery
picam2 = Picamera2()
picam2.start()

while True:
    # Uzyskanie obrazu z kamery
    frame = picam2.capture_array()

    # Konwersja obrazu do przestrzeni HSV
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Dla zielonego koloru (Sprite)
    lowerGreen, upperGreen = get_green_limits()
    maskGreen = cv2.inRange(hsvImage, lowerGreen, upperGreen)

    # Dla czerwonego koloru (Coca-Cola) - od prawdziwego czerwonego
    lowerRed, upperRed = get_red_limits()
    maskRed = cv2.inRange(hsvImage, lowerRed, upperRed)

    # Rozmycie dla wygładzenia wyników i eliminowania szumów
    maskGreen = cv2.GaussianBlur(maskGreen, (5, 5), 0)
    maskRed = cv2.GaussianBlur(maskRed, (5, 5), 0)

    # Liczenie liczby białych pikseli w masce
    non_zero_pixels_green = np.count_nonzero(maskGreen)
    non_zero_pixels_red = np.count_nonzero(maskRed)

    # Załóżmy, że minimalna liczba pikseli, które muszą być różne od zera, by uznać obiekt za wykryty, to 1000
    if non_zero_pixels_green > 1000:
        # Wyciąganie konturów dla zielonego koloru
        mask_ = Image.fromarray(maskGreen)
        bbox = mask_.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            # Rysowanie prostokąta wokół wykrytego obiektu
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

            # Wyświetlanie komunikatu w terminalu
            print("Zielona puszka wykryta!")

    if non_zero_pixels_red > 1000:
        # Wyciąganie konturów dla czerwonego koloru
        mask_ = Image.fromarray(maskRed)
        bbox = mask_.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            # Rysowanie prostokąta wokół wykrytego obiektu
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

            # Wyświetlanie komunikatu w terminalu
            print("Czerwona puszka Coca-Cola wykryta!")

    # Wyświetlanie obrazu
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Zamiana przestrzeni kolorów na RGB
    cv2.imshow('frame', frame)

    # Zakończenie pętli po naciśnięciu 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Zwalnianie zasobów
cv2.destroyAllWindows()


