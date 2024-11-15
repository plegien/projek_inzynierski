import numpy as np
import cv2
from picamera2 import Picamera2
from PIL import Image
import time
from color_range import get_green_limits, get_red_limits, get_orange_limits, create_color_mask
from camera_motor import MotorControl


# Pobranie zakresów kolorów dla zielonego i czerwonego
lowerGreen, upperGreen = get_green_limits()
lowerRed, upperRed = get_red_limits()
lowerOrange, upperOrange = get_orange_limits()

# Inicjalizacja silnika
motor = MotorControl(dir_pin=22, step_pin=23, enable_pin=24)
motor_activated = False # Flaga pozwalająca uruchomić silnik ponownie
last_detected_time = None # Czas ostatniej detekcji 
motor.disable_motor() #wyłączenie silnika

# Inicjalizacja kamery
picam2 = Picamera2()
picam2.start()



# Funkcja odpowiedzialna za wykrywanie kolorwych puszek 
def detect_can(mask, color_name, frame, bbox_color=(0, 255, 0), pixel_threshold=1000):

    # Zliczenie pixeli
    non_zero_pixels = np.count_nonzero(mask)

    # Jeżeli ilość wykrytych pixeli jest odpowiednia narysowanie kwadratu na obiekcie
    if non_zero_pixels > pixel_threshold:
        mask_img = Image.fromarray(mask)
        bbox = mask_img.getbbox()
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), bbox_color, 5)
            print(f"{color_name} puszka wykryta!")
        return True
    return False

def manage_motor(motor, motor_activated, last_detected_time, detection_status, activation_delay=1.3):
    if detection_status and not motor_activated:
        motor.enable_motor() #włączenie silnika 

        # Działanie silnika (ilość kroków, kierunek, opoźnienie na krok)
        motor.rotate_motor(steps=50, direction=True, step_delay=0.001)

        motor.disable_motor() #wyłączenie silnika 
        return True, time.time()

        # Po odliczeniu czasu można uruchomić silnik ponownie
    elif motor_activated and time.time() - last_detected_time > activation_delay:

        print("Puszka zniknęła, oczekiwanie na ponowne wykrycie.")
        return False, None
    
    return motor_activated, last_detected_time

while True:

    # Uruchomienie kamery
    frame = picam2.capture_array()
    # konwersja obrazu z kamery do BGR (bez tego nie działa HSV)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    # Konwersja obrazu do HSV
    hsvImage = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    
    # Tworzenie masek 
    maskGreen = create_color_mask(hsvImage, lowerGreen, upperGreen)
    maskOrange = create_color_mask(hsvImage, lowerOrange, upperOrange)
    maskRed = create_color_mask(hsvImage, lowerRed, upperRed)

    # Detekcja kolorowych puszek 
    zielona_wykryta = detect_can(maskGreen, "Zielona", frame, (0, 255, 0))
    czerwona_wykryta = detect_can(maskRed, "Czerwona", frame, (255, 0, 0))
    pomaranczowa_wykryta = detect_can(maskOrange, "Pomaranczowa", frame, (255, 165, 0))
    
    
    motor_activated, last_detected_time = manage_motor(
        motor, motor_activated, last_detected_time, zielona_wykryta
    )

    # Konwersja obrazu z kamery do RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Podgląd masek 
    #cv2.imshow('frame_green', maskGreen)
    #cv2.imshow('frame_red', maskRed)
    #cv2.imshow('frame_orange', maskOrange)

    # Podgląd z kamery
    cv2.imshow('frame', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Zwolnienie zasobów (kamera, okna, silnik)
cv2.destroyAllWindows()
motor.disable_motor()
picam2.stop()
