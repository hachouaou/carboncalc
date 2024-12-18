import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_data():
    """
    Charge les différentes données et les retourne.
    """
    aliments = pd.read_csv("../data/aliments_final.csv")
    equipements = pd.read_csv("../data/equipements_filtered.csv")
    energie = pd.read_csv("../data/energie_filtered.csv")

    return aliments, equipements, energie

def get_user_selection_energie(data):
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

def get_user_selection_aliments(data):

    total_co2 = 0
    while True:
        print("\n === Sélection des Aliments ===")
        categories = data['main_type'].unique()
        for idx, cat in enumerate(categories, 1):
            print(f"{idx}. {cat}")
        print("0. Terminer la sélection")

        try:
            choice_cat = int(input("Choisissez une catégorie : "))
            if choice_cat == 0:
                return 0
            selected_cat = categories[choice_cat - 1]

            # Exceptions pour certaines catégories
            if selected_cat in ['Glaces et sorbets', 'Matières grasses', 'Aliments infantiles']:
                produits = data[data['main_type'] == selected_cat]
                options = list(produits['nom'])
                co2_values = list(produits['CO2'])

                for idx, option in enumerate(options, 1):
                    print(f"{idx}. {option} ({co2_values[idx-1]} kgCO2/unité)")
                choice_prod = int(input("Choisissez un produit : "))
                quantity = float(input(f"Quantité en unité du produit ({options[choice_prod-1]}) : "))
                total_co2 += quantity * co2_values[choice_prod - 1]
                continue

            # Processus normal pour les sous_catégories
            sous_categories = data[data['categorie'] == selected_cat]['sous_categorie'].unique()

            for idx, sous_cat in enumerate(sous_categories, 1):
                print(f"{idx}. {sous_cat}")
            choice_sous_cat = int(input("Choisissez un sous-type : "))
            selected_sous_cat = sous_categories[choice_sous_cat - 1]

            produits = data[(data['categorie'] == selected_cat) & (data['sous_categorie'] == selected_sous_cat)]
            options = list(produits['nom'])
            co2_values = list(produits['CO2'])

            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option} ({co2_values[idx-1]} kgCO₂/unité)")
            choice_prod = int(input("Choisissez un produit : "))
            quantity = float(input(f"Quantité en unités ({options[choice_prod-1]}) : "))
            total_co2 += quantity * co2_values[choice_prod - 1]
        except (ValueError, IndexError):
            print("Entrée invalide, réessayez.")
            return 0
    return total_co2

def get_user_selection_equipements(data):
    print("\n=== Sélection des Équipements ===")
    total_co2 = 0
    options = list(data['nom'])
    co2_values = list(data['CO2'])

    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option} ({co2_values[idx-1]} kgCO₂)")
    print("0. Terminer la sélection")

    while True:
        try:
            choice = int(input("Entrez le numéro de l'équipement ou 0 pour terminer : "))
            if choice == 0:
                break
            if 1 <= choice <= len(options):
                total_co2 += co2_values[choice - 1]
            else:
                print("Numéro invalide, réessayez.")
        except ValueError:
            print("Entrée invalide, réessayez.")
    return total_co2

def main():
    print("=== Bienvenue dans le Calculateur d'Empreinte Carbone ===")
    aliments, equipements, energie = load_data()

    total_energie = get_user_selection_energie(energie)
    total_equipements = get_user_selection_equipements(equipements)
    total_aliments = get_user_selection_aliments(aliments)
    
    total_co2 = total_aliments + total_equipements + total_energie

    print("\n=== Résultats de votre Empreinte Carbone ===")
    print(f"Aliments : {total_aliments:.2f} kgCO₂")
    print(f"Équipements : {total_equipements:.2f} kgCO₂")
    print(f"Énergie : {total_energie:.2f} kgCO₂")
    print("--------------------------------------------")
    print(f"TOTAL : {total_co2:.2f} kgCO₂")

if __name__ == "__main__":
    main()
