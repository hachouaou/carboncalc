import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """
    Charge les différentes données et les retourne.
    """
    aliments = pd.read_csv("../data/aliments_final.csv")
    equipements = pd.read_csv("../data/equipements_filtered.csv")
    energie = pd.read_csv("../data/energie_filtered.csv")

    return aliments, equipements, energie

def get_user_selection_energie(data):
    """
    Retourne le total de co2 émis par l'utilisateur en fonction de l'énergie qu'il utilise.
    """
    print("\nSélectionnez le type d'énergie et entrez la quantité correspondante :")
    total_co2 = 0
    options = list(data['french_name'])
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
    """
    Retourne le total de co2 émis par l'utilisateur en fonction des aliments qu'il utilise.
    """
    total_co2 = 0
    selected_categories = []
    while True:
        print("\n === Sélection des Aliments ===")
        categories = data['main_type'].unique()
        for idx, cat in enumerate(categories, 1):
            print(f"{idx}. {cat}")
        print("0. Terminer la sélection")

        try:
            choice_cat = int(input("Choisissez une catégorie : "))
            if choice_cat == 0:
                break
            selected_cat = categories[choice_cat - 1]
            selected_categories.append(selected_cat)

            # Exceptions pour certaines catégories
            if selected_cat in ['Glaces et sorbets', 'Matières grasses', 'Aliments infantiles']:
                produits = data[data['main_type'] == selected_cat]
                options = list(produits['nom'])
                co2_values = list(produits['CO2'])
                attributs = list(produits['french_attribut'])

                for idx, option in enumerate(options, 1):
                    print(f"{idx}. {option} - {attributs[idx-1]} ({co2_values[idx-1]} kgCO2/unité)")
                choice_prod = int(input("Choisissez un produit : "))
                quantity = float(input(f"Quantité en unité du produit ({options[choice_prod-1]}) : "))
                total_co2 += quantity * co2_values[choice_prod - 1]
                continue

            # Processus normal pour les sous_catégories
            sous_categories = data[data['main_type'] == selected_cat]['sous_type'].unique()

            for idx, sous_cat in enumerate(sous_categories, 1):
                print(f"{idx}. {sous_cat}")
            choice_sous_cat = int(input("Choisissez un sous_type : "))
            selected_sous_cat = sous_categories[choice_sous_cat - 1]

            produits = data[(data['main_type'] == selected_cat) & (data['sous_type'] == selected_sous_cat)]
            options = list(produits['nom'])
            co2_values = list(produits['CO2'])
            attributs = list(produits['french_attribut'])

            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option} - {attributs[idx-1]} ({co2_values[idx-1]} kgCO2/unité)")
            choice_prod = int(input("Choisissez un produit : "))
            quantity = float(input(f"Quantité en unités ({options[choice_prod-1]}) : "))
            total_co2 += quantity * co2_values[choice_prod - 1]
        except (ValueError, IndexError):
            print("Entrée invalide, réessayez.")
            return 0
    return total_co2, selected_categories

def get_user_selection_equipements(data):
    """
    Retourne le total de co2 émis par l'utilisateur en fonction des équipements qu'il utilise.
    """
    print("\n=== Sélection des Équipements ===")
    total_co2 = 0
    options = list(data['nom'])
    co2_values = list(data['CO2'])

    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option} ({co2_values[idx-1]} kgCO2)")
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

def plot_pie_charts(aliments, total_aliments, total_equipements, total_energie, selected_categories):
    """
    Affiche 2 pie plots pour montrer le portions de CO2 de l'utilisateur.
    """
    #1er camembert : portion de chaque total
    labels_totals = ['Aliments', 'Equipements', "Energie"]
    values_totals = [total_aliments, total_equipements, total_energie]

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.pie(
        values_totals, labels=labels_totals, colors=sns.color_palette('pastel')
        )
    plt.title('Portion de chaque sourced\'émission de CO2')

    #2eme camembert : portion de chaque catégorie d'aliment

    filtered_aliments = aliments[aliments['main_type'].isin(selected_categories)]
    categorie_totals = filtered_aliments.groupby('main_type')['CO2'].sum()
    labels_categories = categorie_totals.index
    values_categories = categorie_totals.values

    plt.subplot(1, 2, 2)
    plt.pie(values_categories, labels=labels_categories, colors=sns.color_palette('pastel'))
    plt.title("Portion des émissions par catégorie d'aliments sélectionnée")

    plt.tight_layout()
    plt.show()

def main():
    print("=== Bienvenue dans le Calculateur d'Empreinte Carbone ===")
    aliments, equipements, energie = load_data()

    total_energie = get_user_selection_energie(energie)
    total_equipements = get_user_selection_equipements(equipements)
    total_aliments, selected_categories = get_user_selection_aliments(aliments)

    total_co2 = total_aliments + total_equipements + total_energie

    print("\n=== Résultats de votre Empreinte Carbone ===")
    print(f"Aliments : {total_aliments:.2f} kgCO2")
    print(f"Équipements : {total_equipements:.2f} kgCO2")
    print(f"Énergie : {total_energie:.2f} kgCO2")
    print("--------------------------------------------")
    print(f"TOTAL : {total_co2:.2f} kgCO2")

    plot_pie_charts(aliments, total_aliments, total_equipements, total_energie, selected_categories)
if __name__ == "__main__":
    main()
