import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_data():

    #aliments = pd.read_csv("../data/aliments.csv")
    #equipements = pd.read_csv("../data/equipements.csv")
    energie = pd.read_csv("../data/energie.csv")

    """aliments_filtered = aliments.drop(["english_name", "french_attribut", 'id', "english_attribut", 
                                                        "french_tag", "english_tag", "comment", "sous_type", "status", "type", 
                                                        "validity_range", "unit"], axis=1)

    equipements_filtered = equipements.drop(['french_name', 'status', 'type', 'english_name', 'french_attribut', 
                                            'english_attribut', 'english_tag', 'unit', 'validity_range', 'comment', 
                                            'french_tag', 'id'], axis=1)"""

    energie_filtered = energie.drop(['status', 'id', 'english_name', 'french_attribut', 'english_attribut', 'type', 'french_tag', 
                                     'english_tag', 'validity_range', 'comment', 'unit'], axis = 1).rename(columns={"french_name" : "nom"})
    
    return energie_filtered

def get_user_selection(data):
    print("\nSélectionnez le type d'énergie et entrez la quantité correspondante :")
    total_co2 = 0
    options = list(data['nom'])
    units = list(data['CO2'])
    
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option} ({units[idx-1]} kgCO₂/unité)")
    print("0. Terminer la sélection")
    
    while True:
        try:
            choice = int(input("Entrez le numéro de l'élément ou 0 pour terminer : "))
            if choice == 0:
                break
            if 1 <= choice <= len(options):
                quantity = float(input(f"Quantité en unités ({options[choice-1]}) : "))
                total_co2 += quantity * units[choice-1]
            else:
                print("Numéro invalide, réessayez.")
        except ValueError:
            print("Entrée invalide, réessayez.")
    return total_co2

def main():
    print("=== Bienvenue dans le Calculateur d'Empreinte Carbone pour l'Énergie ===")
    energie = load_data()
    total_energie = get_user_selection(energie)
    
    print("\n=== Résultats de votre Empreinte Carbone ===")
    print(f"Énergie : {total_energie:.2f} kgCO₂")
    print("--------------------------------------------")
    print(f"TOTAL : {total_energie:.2f} kgCO₂")

if __name__ == "__main__":
    main()
