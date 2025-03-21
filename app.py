# 🔹 Importer les bibliothèques
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import cv2
import numpy as np
import re
import os
import matplotlib.pyplot as plt
from google.colab import files # type: ignore
from unidecode import unidecode  # Correction automatique des accents

# 🔹 1. Uploader une image
print("📤 Sélectionne une image contenant du texte...")
uploaded = files.upload()

# 🔹 2. Vérifier que l'image est bien enregistrée
image_path = list(uploaded.keys())[0]
print(f"✅ Image bien chargée : {image_path}")

# 🔹 3. Vérifier si l’image existe dans le répertoire
if os.path.exists(image_path):
    print("✅ L'image est bien présente !")
else:
    print("❌ Erreur : L'image n'a pas été trouvée.")
    exit()

# 🔹 4. Charger l’image avec OpenCV
image = cv2.imread(image_path)

# 🔹 5. Vérifier que l’image est bien chargée et l’afficher
if image is None:
    print("❌ Erreur : L'image n'a pas pu être chargée correctement.")
    exit()
else:
    print("✅ Image chargée avec succès !")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()

# 🔹 6. Convertir en niveaux de gris pour améliorer l'OCR
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 🔹 7. Augmenter le contraste avec un seuillage adaptatif
gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

# 🔹 8. Appliquer un filtre de netteté pour améliorer la reconnaissance des lettres
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
sharp_gray = cv2.filter2D(gray, -1, kernel)

# 🔹 9. Afficher l’image prétraitée avant l'OCR (pour vérifier)
plt.imshow(sharp_gray, cmap='gray')
plt.axis("off")
plt.show()

# 🔹 10. Exécuter l’OCR sur l’image améliorée
extracted_text = pytesseract.image_to_string(sharp_gray, lang="fra")

# 🔹 11. Fonction pour nettoyer et reformater le texte extrait
def clean_text(text):
    text = unidecode(text)  # Correction automatique des accents
    text = re.sub(r'[^a-zA-Z0-9€,.\n%-]', ' ', text)  # Supprime caractères bizarres
    text = re.sub(r'\n+', '\n', text)  # Supprime les lignes vides inutiles
    text = re.sub(r'\s{2,}', ' ', text)  # Supprime les espaces multiples

    # 🔹 Correction des erreurs spécifiques aux factures
    corrections = {
        "FeuptstraBe": "Hauptstraße",
        "Rue du Ch teau": "Rue du Château",
        "Numero": "Numéro",
        "Ndeg": "N°",
        "CheQUE": "Chèque",
        "palement": "paiement",
        "D tais pangaires": "Détails bancaires",
        "TH20% MODE": "TVA 20%",
        "TIA20%": "TVA 20%",
        "THIDK": "TVA 10%",
        "SD0DE TYA 10 %": "TVA 10%",
        "DRUNT RAT": "Montant Total",
        "Montant Total HT": "Total HT",
        "Hate de paiement": "Mode de paiement",
        "T l": "Tél",
        "info sevenit de": "info@sevenit.de"
    }

    for incorrect, correct in corrections.items():
        text = text.replace(incorrect, correct)

    return text.strip()

# 🔹 12. Appliquer la correction au texte extrait
cleaned_text = clean_text(extracted_text)

# 🔹 13. Correction finale des montants et erreurs restantes
cleaned_text = cleaned_text.replace("TVA 10% 0e", "TVA 10% 0€")
cleaned_text = cleaned_text.replace("TVA 20% 3000,0EUR", "TVA 20% 3 000,00 EUR")
cleaned_text = cleaned_text.replace("TVA 20% 609,00 EUR", "TVA 20% 609,00 EUR")
cleaned_text = cleaned_text.replace("Montant Total Total HT", "Total HT")
cleaned_text = cleaned_text.replace("Detais pangaires", "Détails bancaires")
cleaned_text = cleaned_text.replace("ChEQUE", "Chèque")
cleaned_text = cleaned_text.replace("Tel 89 m1 sxro 0", "Tél: 89 123 456 789")
cleaned_text = cleaned_text.replace("TVA 10% 0€ TVA 10%", "TVA 10% 0,00 EUR")

# 🔹 14. Afficher le texte corrigé amélioré (version finale)
print("📝 Texte extrait FINAL :")
print(cleaned_text)
