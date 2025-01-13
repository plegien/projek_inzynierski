import cv2
import numpy as np
import matplotlib.pyplot as plt



images = [
    cv2.imread('puszka_niebieska_przod0.jpg'),
    cv2.imread('puszka_niebieska_bok0.jpg'),
    cv2.imread('puszka_niebieska0.jpg')
]

# Przekształcenie obrazów do przestrzeni HSV
hsv_images = [cv2.cvtColor(img, cv2.COLOR_BGR2HSV) for img in images]

# Ustalenie zakresu HSV dla wykrywania koloru obiektu
lower_red = np.array([98, 249, 148])
upper_red = np.array([114, 255, 254])

# Obliczanie maski i histogramów dla każdego obrazu
masks = [cv2.inRange(hsv, lower_red, upper_red) for hsv in hsv_images]
hue_hists = [cv2.calcHist([hsv], [0], mask, [256], [0, 256]) for hsv, mask in zip(hsv_images, masks)]
saturation_hists = [cv2.calcHist([hsv], [1], mask, [256], [0, 256]) for hsv, mask in zip(hsv_images, masks)]
value_hists = [cv2.calcHist([hsv], [2], mask, [256], [0, 256]) for hsv, mask in zip(hsv_images, masks)]

# Rysowanie histogramów dla Hue
plt.figure(figsize=(12, 4))
lighting_conditions = ['Oświetlenie zza kamery', 'Oświetlenie z boku', 'Oświetlenie z przodu']
for i, hue_hist in enumerate(hue_hists):
    plt.subplot(1, 3, i + 1)
    plt.plot(hue_hist)
    plt.title(f'Hue Histogram - {lighting_conditions[i]}')
plt.tight_layout()
plt.show()

# Rysowanie histogramów dla Saturation
plt.figure(figsize=(12, 4))
for i, saturation_hist in enumerate(saturation_hists):
    plt.subplot(1, 3, i + 1)
    plt.plot(saturation_hist)
    plt.title(f'Saturation Histogram - {lighting_conditions[i]}')
plt.tight_layout()
plt.show()

# Rysowanie histogramów dla Value
plt.figure(figsize=(12, 4))
for i, value_hist in enumerate(value_hists):
    plt.subplot(1, 3, i + 1)
    plt.plot(value_hist)
    plt.title(f'Value Histogram - {lighting_conditions[i]}')
plt.tight_layout()
plt.show()
