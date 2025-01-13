import numpy as np
import cv2
from picamera2 import Picamera2


def select_roi_bgr(frame, roi_number):

    roi = cv2.selectROI(f"Select ROI for Color {roi_number}", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow(f"Select ROI for Color {roi_number}")
    return roi

# Funkcja do obliczania zakresów HSV na podstawie BGR
def calculate_hsv_range_from_bgr(frame, roi):
    x, y, w, h = roi
    roi_frame = frame[y:y+h, x:x+w]

    # Konwersja regionu z BGR do HSV
    hsv_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2HSV)

    # Obliczanie minimalnych i maksymalnych wartości HSV
    h_min = np.min(hsv_roi[:, :, 0])
    h_max = np.max(hsv_roi[:, :, 0])
    s_min = np.min(hsv_roi[:, :, 1])
    s_max = np.max(hsv_roi[:, :, 1])
    v_min = np.min(hsv_roi[:, :, 2])
    v_max = np.max(hsv_roi[:, :, 2])

    # Tworzenie zakresów
    lower_bound = np.array([h_min, s_min, v_min])
    upper_bound = np.array([h_max, s_max, v_max])

    return lower_bound, upper_bound

# Inicjalizacja kamery
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(raw ={"size": (800, 600)},main={"format":'RGB888',"size": (800, 600)}))
picam2.start()

hsv_ranges = []

# Zbieranie zakresów dla 3 kolorów
for i in range(1, 4):
    frame = picam2.capture_array()  
    cv2.imshow("Obraz z kamery", frame)  
    cv2.waitKey(1)

    print(f"Zaznacz region dla Koloru {i} na obrazie.")

    # Wybór regionu ROI dla i-tego koloru
    roi = select_roi_bgr(frame, i)
   
    # Obliczanie zakresów HSV na podstawie BGR w wybranym regionie
    lower_hsv, upper_hsv = calculate_hsv_range_from_bgr(frame, roi)
    print(f"Zakres HSV dla Koloru {i}:\nDolny: {lower_hsv}\nGórny: {upper_hsv}")
    hsv_ranges.append((lower_hsv.tolist(), upper_hsv.tolist()))

# Zapisanie zakresów do pliku
with open("hsv_ranges.txt", "w") as file:
    for i, (lower_hsv, upper_hsv) in enumerate(hsv_ranges, start=1):
        file.write(f"Lower HSV (Color {i}): {lower_hsv}\n")
        file.write(f"Upper HSV (Color {i}): {upper_hsv}\n")

cv2.destroyAllWindows()
picam2.stop()
