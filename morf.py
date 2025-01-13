import cv2
import numpy as np
import matplotlib.pyplot as plt

# Wczytanie trzech obrazów reprezentujących różne warunki oświetleniowe
image_backlight = cv2.imread('puszka_niebieska0.jpg')  # Oświetlenie zza kamery
image_side = cv2.imread('puszka_niebieska_bok0.jpg')   # Oświetlenie z boku
image_front = cv2.imread('puszka_niebieska_przod0.jpg') # Oświetlenie z przodu

# Ustalenie zakresu HSV dla wykrywania koloru obiektu (przykład dla czerwonego koloru)
lower_red = np.array([98, 249, 148])
upper_red = np.array([114, 255, 254])

# Funkcja do wykrywania obiektów na obrazie i wykonywania operacji morfologicznych
def process_mask(image, lower_bound, upper_bound, kernel_size=5):
    # Konwersja obrazu do przestrzeni HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Tworzenie maski dla określonego zakresu koloru
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Tworzenie jądra do operacji morfologicznych
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Operacje morfologiczne
    eroded = cv2.erode(mask, kernel, iterations=1)
    dilated = cv2.dilate(mask, kernel, iterations=1)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask, eroded, dilated, opened, closed

# Funkcja do obliczania IoU (Intersection over Union)
def calculate_iou(predicted_mask, ground_truth_mask):
    intersection = np.sum((predicted_mask == 255) & (ground_truth_mask == 255))
    union = np.sum((predicted_mask == 255) | (ground_truth_mask == 255))
    return intersection / union if union != 0 else 0

# Przetwarzanie obrazów w różnych warunkach oświetleniowych
backlight_mask, backlight_eroded, backlight_dilated, backlight_opened, backlight_closed = process_mask(image_backlight, lower_red, upper_red)
side_mask, side_eroded, side_dilated, side_opened, side_closed = process_mask(image_side, lower_red, upper_red)
front_mask, front_eroded, front_dilated, front_opened, front_closed = process_mask(image_front, lower_red, upper_red)

# Zdefiniowanie "maski wzorcowej" (maski po dylatacji z obrazu z przodu)
ideal_backlight_dilated = backlight_dilated
ideal_side_dilated = side_dilated
ideal_front_dilated = front_dilated

# Obliczanie IoU dla oryginalnych masek
iou_backlight_original = calculate_iou(backlight_mask, ideal_backlight_dilated)
iou_side_original = calculate_iou(side_mask, ideal_side_dilated)
iou_front_original = calculate_iou(front_mask, ideal_front_dilated)

# Obliczanie IoU dla operacji morfologicznych (porównanie z maską wzorcową)
iou_backlight_eroded = calculate_iou(backlight_eroded, ideal_backlight_dilated)
iou_backlight_dilated = calculate_iou(backlight_dilated, ideal_backlight_dilated)
iou_backlight_opened = calculate_iou(backlight_opened, ideal_backlight_dilated)
iou_backlight_closed = calculate_iou(backlight_closed, ideal_backlight_dilated)

iou_side_eroded = calculate_iou(side_eroded, ideal_side_dilated)
iou_side_dilated = calculate_iou(side_dilated, ideal_side_dilated)
iou_side_opened = calculate_iou(side_opened, ideal_side_dilated)
iou_side_closed = calculate_iou(side_closed, ideal_side_dilated)

iou_front_eroded = calculate_iou(front_eroded, ideal_front_dilated)
iou_front_dilated = calculate_iou(front_dilated, ideal_front_dilated)
iou_front_opened = calculate_iou(front_opened, ideal_front_dilated)
iou_front_closed = calculate_iou(front_closed, ideal_front_dilated)

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Wyświetlanie wyników dla każdego warunku oświetleniowego w osobnej figurze z układem 2x3

# Oświetlenie zza kamery (backlight)
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
fig.suptitle('Oświetlenie zza kamery')

axes[0, 0].imshow(cv2.cvtColor(image_backlight, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title(f'Obraz\n(Dylatacja IoU: {iou_backlight_dilated:.2f})')
axes[0, 0].axis('off')
axes[0, 1].imshow(backlight_mask, cmap='gray')
axes[0, 1].set_title(f'Maska\n(IoU: {iou_backlight_original:.2f})')
axes[0, 1].axis('off')
axes[0, 2].imshow(backlight_eroded, cmap='gray')
axes[0, 2].set_title(f'Erozja\n(IoU: {iou_backlight_eroded:.2f})')
axes[0, 2].axis('off')
axes[1, 0].imshow(backlight_dilated, cmap='gray')
axes[1, 0].set_title(f'Dylatacja\n(IoU: {iou_backlight_dilated:.2f})')
axes[1, 0].axis('off')
axes[1, 1].imshow(backlight_opened, cmap='gray')
axes[1, 1].set_title(f'Otwarcie\n(IoU: {iou_backlight_opened:.2f})')
axes[1, 1].axis('off')
axes[1, 2].imshow(backlight_closed, cmap='gray')
axes[1, 2].set_title(f'Zamknięcie\n(IoU: {iou_backlight_closed:.2f})')
axes[1, 2].axis('off')
plt.tight_layout()
plt.show()

# Oświetlenie z boku (side)
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
fig.suptitle('Oświetlenie z boku')

axes[0, 0].imshow(cv2.cvtColor(image_side, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title(f'Obraz\n(Dylatacja IoU: {iou_side_dilated:.2f})')
axes[0, 0].axis('off')
axes[0, 1].imshow(side_mask, cmap='gray')
axes[0, 1].set_title(f'Maska\n(IoU: {iou_side_original:.2f})')
axes[0, 1].axis('off')
axes[0, 2].imshow(side_eroded, cmap='gray')
axes[0, 2].set_title(f'Erozja\n(IoU: {iou_side_eroded:.2f})')
axes[0, 2].axis('off')
axes[1, 0].imshow(side_dilated, cmap='gray')
axes[1, 0].set_title(f'Dylatacja\n(IoU: {iou_side_dilated:.2f})')
axes[1, 0].axis('off')
axes[1, 1].imshow(side_opened, cmap='gray')
axes[1, 1].set_title(f'Otwarcie\n(IoU: {iou_side_opened:.2f})')
axes[1, 1].axis('off')
axes[1, 2].imshow(side_closed, cmap='gray')
axes[1, 2].set_title(f'Zamknięcie\n(IoU: {iou_side_closed:.2f})')
axes[1, 2].axis('off')
plt.tight_layout()
plt.show()

# Oświetlenie z przodu (front)
fig, axes = plt.subplots(2, 3, figsize=(12, 8))
fig.suptitle('Oświetlenie z przodu')

axes[0, 0].imshow(cv2.cvtColor(image_front, cv2.COLOR_BGR2RGB))
axes[0, 0].set_title(f'Obraz\n(Dylatacja IoU: {iou_front_dilated:.2f})')
axes[0, 0].axis('off')
axes[0, 1].imshow(front_mask, cmap='gray')
axes[0, 1].set_title(f'Maska\n(IoU: {iou_front_original:.2f})')
axes[0, 1].axis('off')
axes[0, 2].imshow(front_eroded, cmap='gray')
axes[0, 2].set_title(f'Erozja\n(IoU: {iou_front_eroded:.2f})')
axes[0, 2].axis('off')
axes[1, 0].imshow(front_dilated, cmap='gray')
axes[1, 0].set_title(f'Dylatacja\n(IoU: {iou_front_dilated:.2f})')
axes[1, 0].axis('off')
axes[1, 1].imshow(front_opened, cmap='gray')
axes[1, 1].set_title(f'Otwarcie\n(IoU: {iou_front_opened:.2f})')
axes[1, 1].axis('off')
axes[1, 2].imshow(front_closed, cmap='gray')
axes[1, 2].set_title(f'Zamknięcie\n(IoU: {iou_front_closed:.2f})')
axes[1, 2].axis('off')
plt.tight_layout()
plt.show()

