import cv2
import numpy as np
from picamera2 import Picamera2

# Inicjalizacja kamery Pi
picam2 = Picamera2()

# Uruchomienie kamery
picam2.start()

while True:
    # Przechwycenie obrazu z kamery (domyślnie RGB)
    frame = picam2.capture_array()

    # Konwersja obrazu z RGB (PiCamera) na BGR (OpenCV)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Konwersja obrazu z przestrzeni BGR do HSV
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # Definicja szerszego zakresu dla koloru żółtego w przestrzeni HSV
    lower_yellow = np.array([20, 100, 50], dtype=np.uint8)  # Zwiększenie nasycenia i wartości
    upper_yellow = np.array([25, 255, 255], dtype=np.uint8)

    # Tworzenie maski na podstawie zakresu kolorów
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    # Pokazanie wyniku maski (gdzie żółty będzie biały, reszta czarna)
    cv2.imshow("Yellow Color Detection", mask)

    # Sprawdzanie, czy naciśnięto 'q' w celu zakończenia programu
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Zakończenie pracy kamery i zamknięcie okien
picam2.stop()
cv2.destroyAllWindows()
