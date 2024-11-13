import numpy as np

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
