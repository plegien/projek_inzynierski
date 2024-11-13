import numpy as np
import cv2
from picamera2 import Picamera2
from PIL import Image
from color_range import get_green_limits, get_red_limits
from camera_motor import MotorControl
import time

# Pobranie zakresów kolorów dla zielonego i czerwonego
lowerGreen, upperGreen = get_green_limits()
lowerRed, upperRed = get_red_limits()

print("Zielony limit:", lowerGreen, upperGreen)
print("Czerwony limit:", lowerRed, upperRed)

motor = MotorControl(dir_pin=22, step_pin=23, enable_pin=24)
motor_activated = False  # Flaga kontrolująca stan silnika
last_detected_time = None  # Czas ostatniej detekcji puszki

# Inicjalizacja kamery
picam2 = Picamera2()
picam2.start()

while True:
    # Uzyskanie obrazu z kamery
    frame = picam2.capture_array()

    # Konwersja obrazu do przestrzeni HSV
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Maski kolorów dla zielonego (Sprite) i czerwonego (Coca-Cola)
    maskGreen = cv2.inRange(hsvImage, lowerGreen, upperGreen)
    maskRed = cv2.inRange(hsvImage, lowerRed, upperRed)

    # Rozmycie dla wygładzenia wyników i eliminowania szumów
    maskGreen = cv2.GaussianBlur(maskGreen, (5, 5), 0)
    maskRed = cv2.GaussianBlur(maskRed, (5, 5), 0)

    # Liczenie liczby białych pikseli w masce
    non_zero_pixels_green = np.count_nonzero(maskGreen)
    non_zero_pixels_red = np.count_nonzero(maskRed)

    # Jeśli liczba pikseli zielonego koloru przekroczy próg, oznacza to, że puszka jest wykryta
    if non_zero_pixels_green > 1200:
        # Wyciąganie konturów dla zielonego koloru
        mask_ = Image.fromarray(maskGreen)
        bbox = mask_.getbbox()

        if bbox is not None:
            x1, y1, x2, y2 = bbox
            # Rysowanie prostokąta wokół wykrytego obiektu
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)

            # Wyświetlanie komunikatu w terminalu
            print("Zielona puszka wykryta!")

            # Uruchomienie silnika tylko jeśli jeszcze nie był aktywowany
            if not motor_activated:
                motor.rotate_motor(steps=200, direction=True, step_delay=0.001)
                motor_activated = True  # Ustawienie flagi, żeby nie uruchamiać silnika ponownie

            # Zapamiętanie czasu ostatniego wykrycia puszki
            last_detected_time = time.time()
    
    else:
        # Jeśli puszka zniknęła, sprawdzamy, czy minęło trochę czasu
        if motor_activated and last_detected_time is not None:
            time_since_detection = time.time() - last_detected_time
            if time_since_detection > 1.3:  # Jeśli minęło więcej niż 1.5 sekundy
                motor_activated = False  # Resetowanie flagi, żeby silnik mógł uruchomić się przy nowej detekcji
                print("Puszka zniknęła, oczekiwanie na ponowne wykrycie.")
    
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
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow('frame', frame)

    # Zakończenie pętli po naciśnięciu 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Zwalnianie zasobów
cv2.destroyAllWindows()
motor.disable_motor()  # Wyłączenie silnika po zakończeniu działania
