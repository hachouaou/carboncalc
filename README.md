# README

Ce fichier décrit le projet **carbsimulator** qui vise à créer un package python permettant à un professionel de la restauration d'évaluer l'empreinte carbone de son activité.

## Installation

Pour exécuter les scripts dans ce fichier certaines bibliothèques python sont nécessaires, exécuter la commande suivante dans le dossier téléchargé avec votre env python activé avant de commencer :
```
pip install .
```

## Utilisation

Le script principal est dans le fichier `carbsimulator/calculator.py`. Pour l'utiliser exécuter :
```
python carbsimulator/calculator.py
```
et suivez les instructions !

Le programme commence par le choix du type d'énergie utilisée, l'utilisateur entre ensuite la quantité qu'il utilise. Ensuite, il doit choisir son équipements.
Le programme continue ensuite sur la quantités de chaque aliments. Il commence par choisir le type d'aliments, ensuite le sous-type puis finit enfin par entrer la quantité du prouit choisi.
Le prgramme finit ensuite par donner le total de chaque catégorie (aliments, equipements et energie) et retourne 2 camembert, le premier qui donne la proportion de chaque catégorie, et le deuxième de chaque type d'aliments.

Au vu du nombre conséquent d'aliments, cette approche m'a paru être la plus efficace. De plus, certains types d'aliments ont été traité et permettent de voir la portée du travail qui aurait pu être fait pour un maximum de précision.
