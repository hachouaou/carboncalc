import os
import pandas as pd

def load_raw_data():
    """
    Charge les données brutes
    """

    aliments = pd.read_csv("../data/aliments.csv")
    equipements = pd.read_csv("../data/equipements.csv")
    energie = pd.read_csv("../data/energie.csv")

    return aliments, equipements, energie

def equipements_filtering(equipements):
    """
    Filtre les données des équipements en supprimant les colonnes inutiles
    """

    equipements_filtered = equipements.drop(
    ['french_name', 'status', 'type', 'english_name', 'french_attribut', 'english_attribut',
     'english_tag', 'unit', 'validity_range', 'comment', 'french_tag', 'id'], axis=1
     ).rename(columns={"complete_name" : "nom"}).head()

    return equipements_filtered

def energie_filtering(energie):
    """
    Filtre les données des énergies en supprimant les colonnes inutiles
    """

    energie_filtered = energie.drop(
    ['status', 'id', 'english_name', 'french_attribut', 'english_attribut', 'type',
    'french_tag', 'english_tag', 'validity_range', 'comment'], axis = 1
    )
    energie_filtered = energie_filtered.rename(columns={"french_name" : "nom"})

    return energie_filtered


def aliments_filtering(aliments):
    """
    Filtre les données des aliments en supprimant les colonnes inutiles.
    On supprimes aussi les viandes cuites car un restaurateur aurait plus tendance
    à acheter de la viande crue que de la viande déjà cuite.
    """

    # Renomme la colonne french_name en nom
    aliments_filtered = aliments.rename(columns={"french_name" : "nom"})

    # Supprime les doublons potentiels
    aliments_filtered = aliments_filtered.drop_duplicates(
        subset=aliments_filtered.columns.difference(['id']))

    # Supprime les colonnes inutiles
    aliments_filtered = aliments_filtered.drop(
        ['id', 'status', 'english_name', 'english_attribut', 'type', 'french_tag', 'english_tag',
        'validity_range', 'comment', 'unit'], axis =1)

    # Filtre les lignes où 'french_tag' contient 'viandes cuites'
    aliments_filtered = aliments_filtered[~aliments_filtered['french_tag'].str.contains(
        'viandes cuites', case=False, na=False)]


    return aliments_filtered

def merge_attributs(group):
    """
    Fonction permettant de fusionner les attributs.
    """
    # Vérifie si le groupe contient plus d'une ligne
    if len(group) > 1:
        # Concatène les différents attributs en un, séparés d'un '-'
        merged_attribut = "-".join(group['french_attribut'])

        # Crée un DataFrame avec les valeurs consolidées
        return pd.DataFrame({
            'nom': [group['nom'].iloc[0]],
            'french_attribut': [merged_attribut],
            'CO2': [group['CO2'].iloc[0]],
            'main_type': [group['main_type'].iloc[0]]
        })
    return pd.DataFrame(group)

def aliments_final(aliments_filtered):
    """
    Fonctions regroupant plusieurs opérations faites sur le nettoyage de la base de données aliments.
    Ces opérations sont expliquer au fur et à mesur.
    """
    # Groupe les aliments par leur nom, attributs et le CO2 en ne gardant uniquement que la 1ere occurence
    aliments_grouped = aliments_filtered.groupby(
        ['nom', 'french_attribut', 'CO2'], as_index=False).first()

    # Effectue un seconde groupement par nom et leur attribut
    aliments_final = aliments_grouped.groupby(['nom', 'french_attribut'], as_index=False).agg({
        'CO2': lambda x: round(x.mean(), 2), # Si plusieurs lignes existent on calcule la moyenne
        'main_type': 'first',  # Ici on garde la première valeur de main_type de façon arbitraire
        'sous_type': 'first'   # Ici on garde la première valeur de sous_type de façon arbitraire
    })

    # Filtre les lignes où les aliments sont cuits
    aliments_final = aliments_final[~aliments_final['french_attribut'].str.contains(
        r'\bcuit(?:e|es|s)?\b', case=False, na=False)]

    # Fusionne les attributs
    aliments_final = aliments_final.groupby(['nom', 'CO2'], group_keys=False).apply(merge_attributs)

    # Remplace les différents attributs pour éviter les répetitions
    aliments_final['french_attribut'] = aliments_final['french_attribut'].str.replace(
        r'\bcru(?:e|es|-[^\s]*| pousses pour salades)?\b', 'cru', case=False, regex=True)
    aliments_final['french_attribut'] = aliments_final['french_attribut'].str.replace(
        r'\bpréemballé(?:e|es|-[^\s]*| à réchauffer)?\b', 'préemballé', case=False, regex=True)
    aliments_final['french_attribut'] = aliments_final['french_attribut'].str.replace(
        r'\bsurgelé(?:e|es|-[^\s]*)?\b', 'surgelé', case=False, regex=True)
    aliments_final['french_attribut'] = aliments_final['french_attribut'].str.replace(
        r'\bséché(?:e|es|-[^\s]*)?\b', 'séché', case=False, regex=True)

    # Remplace les differentes catégories pour éviter les répetitions
    aliments_final['main_type'] = aliments_final['main_type'].replace(
        'Fruits, légumes, légumineuses et oléagineux', 'Fruits et Légumes')
    aliments_final['main_type'] = aliments_final['main_type'].replace(
        'Entrées et plats composés', 'Plats composés')
    aliments_final['main_type'] = aliments_final['main_type'].replace(
        'Lait et produits laitiers', 'Produits Laitiers')

    # Ne garde que les différents plat légumes pour enfant
    aliments_final = aliments_final[
        ~((aliments_final['main_type'] == "Aliments infantiles") &
        (~aliments_final['nom'].str.contains("Plat légumes", case=False, na=False)))
    ]

    return aliments_final

def glace_sorbets_filtering(aliments_final):
    """
    Fonction permettant de simplifier les items de type "Glaces et Sorbets".
    Après inspection des données, il n'y avait que trois types de glaces avec des CO2 assez similaires
    et 2 types de Sorbet avec le même CO2.

    Cette fonction permet de donner un aperçu sur le travail qui aurait pu être fait sur l'ensemble des données.
    """
    glaces_sorbets = aliments_final[aliments_final['main_type'] == 'Glaces et sorbets']

    # Calculer la moyenne des glaces
    glaces = glaces_sorbets.iloc[:3]  # Les trois premières lignes sont des glaces
    glaces_avg = {
        'nom': 'Glace',
        'french_attribut': 'type sundae/à partager/bâtonnet-cône',
        'CO2': glaces['CO2'].mean(),
        'main_type': 'Glaces et sorbets'
    }

    # Calculer la moyenne des sorbets
    sorbets = glaces_sorbets.iloc[3:]  # Les deux dernières lignes sont des sorbets
    sorbets_avg = {
        'nom': 'Sorbet',
        'french_attribut': 'en bac/bâtonnet',
        'CO2': sorbets['CO2'].mean(),
        'main_type': 'Glaces et sorbets'
    }

    # Créer un nouveau DataFrame avec les moyennes calculées
    glaces_sorbets_cleaned = pd.DataFrame([glaces_avg, sorbets_avg])

    # Supprimer les anciennes entrées de glaces et sorbets dans la base originale
    aliments_final = aliments_final[aliments_final['main_type'] != 'Glaces et sorbets']

    # Ajouter les nouvelles entrées nettoyées
    aliments_final = pd.concat([aliments_final, glaces_sorbets_cleaned], ignore_index=True)

    # Arrondir le CO2 à 2 chiffres après la virgule
    aliments_final['CO2'] = aliments_final['CO2'].round(2)

    return aliments_final

def chocolat_filtering(aliments_final):
    """
    Fonction permettant de traiter les différents chocolats.
    La base de données présentait plusieurs chocolats sous différents formes avec à chaque fois le même CO2 émis.
    Le regroupement des chocolats permet donc de simplifier le choix de l'utilisateur.
    """
    produits_sucres = aliments_final[aliments_final['main_type'] == 'Produits sucrés']

    # Regrouper les différents types de chocolat
    chocolat_types = ['Chocolat au lait', 'Chocolat noir', 'Chocolat blanc']
    chocolat_grouped = []

    for chocolat in chocolat_types:
        # Filtrer les entrées correspondant à un type spécifique de chocolat, incluant les variantes
        chocolat_entries = produits_sucres[produits_sucres['nom'].str.contains(
            f'^{chocolat}', case=False, na=False)]

        if not chocolat_entries.empty:
            # Vérifier si plusieurs valeurs de CO2 existent
            if chocolat_entries['CO2'].nunique() > 1:
                # Garder uniquement les entrées avec le CO2 le plus fréquent
                correct_co2 = chocolat_entries['CO2'].mode()[0]
                chocolat_entries = chocolat_entries[chocolat_entries['CO2'] == correct_co2]

            # Créer une entrée regroupée pour ce type de chocolat
            chocolat_grouped.append({
                'nom': chocolat,
                'french_attribut': 'tout type',
                'CO2': chocolat_entries['CO2'].iloc[0],
                'main_type': 'Produits sucrés',
                'sous_type': 'Chocolat'

            })

    # Supprimer toutes les anciennes entrées de chocolat dans la base originale
    aliments_final = aliments_final[~((aliments_final['main_type'] == 'Produits sucrés') &
                        (aliments_final['nom'].str.contains(
                            '|'.join(chocolat_types), case=False, na=False)))]

    # Ajouter les nouvelles entrées regroupées
    aliments_final = pd.concat([aliments_final, pd.DataFrame(chocolat_grouped)], ignore_index=True)

    return aliments_final

def matieres_grasses_filtering(aliments_final):
    """
    Fonctions permettant de traiter les aliments de type Matières grasses.
    Toujours dans l'optique de faciliter l'experience de l'utilisateur, certaines données ont été regroupées.
    """
    beurre_group = aliments_final[aliments_final['nom'].str.contains('Beurre', case=False)]
    beurre_aggregated = {
        'nom': 'Beurre (tous types)',
        'french_attribut': ' / '.join(set(beurre_group['french_attribut'])),
        'CO2': beurre_group['CO2'].mean(),
        'main_type': 'Matières grasses'
    }

    # Regrouper les matières grasses végétales
    vegetal_group = aliments_final[aliments_final['nom'].str.contains(
        'Matière grasse végétale', case=False)]
    vegetal_aggregated = {
        'nom': 'Matière grasse végétale (tous types)',
        'french_attribut': ' / '.join(set(vegetal_group['french_attribut'])),
        'CO2': vegetal_group['CO2'].mean(),
        'main_type': 'Matières grasses'

    }

    combined_group = aliments_final[aliments_final['nom'].str.contains(
        'Huile combinée', case=False)]
    combined_aggregated = {
        'nom': 'Huile combinée',
        'french_attribut': ' / '.join(set(combined_group['french_attribut'])),
        'CO2': combined_group['CO2'].mean(),
        'main_type': 'Matières grasses'
    }

    melangee_group = aliments_final[aliments_final['nom'].str.contains(
        'Matière grasse mélangée', case=False)]
    melangee_aggregated = {
        'nom': 'Matière grasse mélangée (végétale et laitière)',
        'french_attribut': ' / '.join(set(combined_group['french_attribut'])),
        'CO2': melangee_group['CO2'].mean(),
        'main_type': 'Matières grasses'
    }

    # Supprimer les anciennes entrées de beurre et matières grasses végétales
    aliments_final = aliments_final[~aliments_final['nom'].str.contains(
        'Beurre|Matière grasse végétale|Huile combinée|Matière grasse mélangée', case=False)]

    # Ajouter les nouvelles entrées regroupées
    aliments_final = pd.concat([aliments_final, pd.DataFrame(
        [beurre_aggregated, vegetal_aggregated, combined_aggregated, melangee_aggregated])],
        ignore_index=True)

    # Arrondir le CO2 à 2 chiffres après la virgule
    aliments_final['CO2'] = aliments_final['CO2'].round(2)

    return aliments_final

def the_filtering(aliments_final):
    the_group = aliments_final[(aliments_final['nom'].str.contains(
        'Thé', case=False)) & (aliments_final['CO2'] == 0.04)]

    # Créer une entrée regroupée pour les thés
    the_aggregated = {
        'nom': 'Thé (tous types)',
        'french_attribut': ' / '.join(set(the_group['french_attribut'])),
        'CO2': 0.04,
        'main_type': 'Boissons'
    }

    # Supprimer les anciennes entrées de thés avec CO2 = 0.04
    aliments_final = aliments_final[~((aliments_final['nom'].str.contains(
        'Thé', case=False)) & (aliments_final['CO2'] == 0.04))]

    # Ajouter la nouvelle entrée regroupée
    aliments_final = pd.concat([aliments_final, pd.DataFrame([the_aggregated])], ignore_index=True)

    return aliments_final

def export_to_csv(aliments_final, energie_filtered, equipements_filtered):
    """
    Fonction permettant d'exporter les nouvelles bases de données après leur différents traitements.
    """
    # Store le path du dossier parent
    parent_dir = os.path.join(os.path.dirname(os.getcwd()), "data")

    # Construire le chemin complet du fichier
    aliment_path = os.path.join(parent_dir, "aliments_final.csv")
    energie_path = os.path.join(parent_dir, "energie_filtered.csv")
    equipements_path = os.path.join(parent_dir, "equipements_filtered.csv")

    try:
        # Exporter la DataFrame en CSV
        aliments_final.to_csv(aliment_path, index=False)
        energie_filtered.to_csv(energie_path, index=False)
        equipements_filtered.to_csv(equipements_path, index=False)
        print(f"Fichier exporté avec succès : {aliment_path}")
    except Exception as e:
        print(f"Erreur lors de l'exportation : {e}")
