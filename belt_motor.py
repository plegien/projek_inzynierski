import numpy as np
import cv2
from picamera2 import Picamera2
from signal import pause
from gpiozero import PWMOutputDevice, Button
from camera_motor import MotorControl
import time

# ustawienia pinów
in1 = PWMOutputDevice(6)  
in2 = PWMOutputDevice(13)  
button = Button(26, bounce_time=0.1)  
belt_running = 0

# stan silnika dc
motor_stop_delay = 3
last_stop_time = 0
motor_running = False

# flagi kolorów
color1_flag = 0
color2_flag = 0
color3_flag = 0

# Inicjalizacja silnika krokowego
motor = MotorControl(dir_pin=22, step_pin=23, enable_pin=24)
motor_activated = False  
last_detected_time = None  
motor.disable_motor()  

# włącz/wyłącz silnik dc
def toggle_motor():
    global motor_running
    if motor_running:
        # włącz silnik dc
        in1.value = 0  
        in2.value = 0  
        print("silnik działa")
    else:
        # wyłącz silnik dc
        in1.value = 0.4  
        in2.value = 0  
        print("silnik jest wyłaczony")

    motor_running = not motor_running

button.when_pressed = toggle_motor

# Funkcja do odczytania zakresów HSV z pliku
def read_hsv_ranges_from_file(file_path="hsv_ranges.txt"):
    hsv_ranges = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):  
            lower_hsv = np.array([int(x) for x in lines[i].strip().split(":")[1].strip()[1:-1].split(",")])
            upper_hsv = np.array([int(x) for x in lines[i+1].strip().split(":")[1].strip()[1:-1].split(",")])
            hsv_ranges.append((lower_hsv, upper_hsv))
    return hsv_ranges

# Funkcja do wykrywania krawędzi, rysowania konturów i śledzenia obiektu
def detect_and_track_objects(frame, mask, color, target_x=420):
    global last_stop_time
    global motor_running
    global motor_stop_delay
    global belt_running

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    object_visible = False 

    for contour in contours:
        if cv2.contourArea(contour) > 1500:  # Ignoruj małe kontury
            x, y, w, h = cv2.boundingRect(contour)
            
            # Rysowanie prostokąta wokół obiektu
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Śledzenie pozycji i wysokości obiektu
            cv2.putText(frame, f"Pos: ({x}, {y})", (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, f"Height: {h}px", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
           
            object_visible = True
            
           
            if x <= target_x and motor_running:
                
                
                in1.value = 0  
                in2.value = 0  
                print("Silnik 1 zatrzymany, pozycja x osiągnęła wymagany poziom.")
                motor_running = False  
                belt_running = 0
                
                last_stop_time = time.time()  

    
    if  not object_visible and (time.time() - last_stop_time) >= motor_stop_delay:
        
        in1.value = 0.4  
        in2.value = 0    
        
        motor_running = True  
        belt_running = 1
        print("Silnik 1 ponownie włączony, taśmociąg rusza.")

    return frame

#W tej funkcji znajdują się operacje morfologiczne pozwalające usunąc szumy z obrazów masek 
def apply_morphological_operations(mask):

    kernel = np.ones((3, 3), np.uint8)


    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel) # usuwa szumy, zapewnia lepsze rozpoznawanie ponieważ nie ma artefaktów na maskach które mogą zostać błednie wykryte
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # usuwa artefakty na obiekcie przez co maska jest dokładniejsza

    #dyltacja, wzmocnienie szczegółów
    #eliminacja zbędnych szczegołow
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)    
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.erode(mask, kernel, iterations=1)

    return mask


# Funkcja do wykrywania kolorów w obrazie
def detect_colors(frame, hsv_ranges):
    global color1_flag, color2_flag, color3_flag  # flagi kolorów

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    masks = []
    detected_color = None  # Zmienna do przechowywania wykrytego koloru

    # Resetowanie flag przed nowym przetwarzaniem
    color1_flag = 0
    color2_flag = 0
    color3_flag = 0

    # Iteracja przez wszystkie zakresy HSV
    for idx, (lower_hsv, upper_hsv) in enumerate(hsv_ranges):
        # Tworzenie maski na podstawie zakresow hsv
        mask = cv2.inRange(hsv_frame, lower_hsv, upper_hsv)
        mask = apply_morphological_operations(mask)  # Stosujemy operacje morfologiczne
        masks.append(mask)

        
        if cv2.countNonZero(mask) > 0:

            # wykrywanie koloru i zaznaczania jego flagi
            if idx == 0: 
                color1_flag = 1
                detected_color = "Color 1"

            if idx == 1:  
                color2_flag = 1
                detected_color = "Color 2"
                
            if idx == 2:  
                color3_flag = 1
                detected_color = "Color 3"

    return masks, detected_color


# właczenie kamery
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(raw ={"size": (800, 600)}, main={"format":'RGB888',"size": (800, 600)}))
picam2.start()

# Odczytanie zakresów HSV z pliku (dla trzech kolorów)
hsv_ranges = read_hsv_ranges_from_file()

# Kolory do rysowania konturów (np. czerwony, zielony, niebieski)
colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # Możesz dodać więcej, jeśli masz więcej zakresów

# pętla głowna programu
while True:
    frame = picam2.capture_array()

    # Wykrywanie kolorów i tworzenie masek
    masks, detected_color = detect_colors(frame, hsv_ranges)

    # Rysowanie konturów i śledzenie obiektów na kopii obrazu
    frame_with_contours = frame.copy()
    for i, (mask, color) in enumerate(zip(masks, colors)):
        
        frame_with_contours = detect_and_track_objects(frame_with_contours, mask, color)
        
    # Wyświetlanie masek dla każdego koloru osobno
    for i, mask in enumerate(masks):
        cv2.imshow(f"Mask {i+1}", mask)

    # Wyświetlanie obrazu z konturami
    cv2.imshow("Camera Feed with Detected Objects", frame_with_contours)

    # Wyświetlanie wykrytego koloru
    if detected_color:
        print(f"Detected: {detected_color}")

    if color1_flag == 1 and belt_running == 0:
        motor.enable_motor()  
        time.sleep(1)
        motor.rotate_motor(steps=50, direction=False, step_delay=0.005) 
        time.sleep(1)
        motor.rotate_motor(steps=50, direction=True, step_delay=0.001)  
        time.sleep(0.2)
        motor.disable_motor()   
   
    elif (color2_flag == 1 or color3_flag == 1) and belt_running == 0:
        motor.enable_motor()  
        motor.rotate_motor(steps=50, direction=True, step_delay=0.005)  
        
        in1.value = 0.4  
        in2.value = 0    
        
        motor_running = True  
        belt_running = 1
        print("Silnik 1 ponownie włączony, taśmociąg rusza.")
        time.sleep(2.5)
        motor.rotate_motor(steps=50, direction=False, step_delay=0.001)  
        time.sleep(0.2)       
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
pause()
