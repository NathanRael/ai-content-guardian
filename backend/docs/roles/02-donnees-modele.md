# 2. Données et modèle

## Ce qu'il faut savoir

Le cœur du système repose sur un jeu de données de référence : `backend/data/labeled_data.csv`, issu du dataset de Davidson et al. sur le discours haineux et le langage offensant. Ce jeu contient des tweets annotés en trois classes : `hate_speech`, `offensive_language` et `neither`.

Le projet travaille sur un déséquilibre de classes important. Dans les données finales, la classe `offensive_language` représente environ 77,4 % des exemples, alors que `hate_speech` n'est que 5,8 %. C'est une donnée importante, car elle explique pourquoi le modèle est évalué sur la macro-F1 et non seulement sur l'accuracy.

Le pipeline de formation est reproductible :

- split 80/20 stratifié ;
- `random_state=42` ;
- TF-IDF avec 3 000 features et 1-2 grams ;
- deux modèles comparés : régression logistique et forêt aléatoire.

Les artefacts sont sauvegardés dans `backend/models/` et `backend/outputs/` : modèles, indices de split, métriques, distribution des classes.

## Ce que le backend confirme

- `backend/train.py` entraîne les modèles et génère les sorties.
- `backend/services/ml_pipeline.py` contient le pipeline de préparation et de sauvegarde.
- `backend/routers/metrics.py` expose les métriques calculées.
- `backend/routers/model_info.py` restitue aussi une synthèse du dataset et de la distribution.

## Points de vigilance

- Le dataset est culturellement et linguistiquement très spécifique.
- Le modèle est moins robuste sur les cas rares comme le discours haineux explicite.
- Un bon pipeline de données ne suffit pas : il faut toujours regarder les limites de généralisation.
- Le modèle ne peut pas être pris comme preuve objective de vérité sur des cas sociaux ou dialectaux.

## Discours d'une minute

Pour ma part, je me suis concentré sur la partie technique du système, notamment la préparation des données et la mise en place du pipeline d'entraînement du modèle.

Concrètement, on part d’un dataset de tweets annotés avec trois catégories : hate_speech, offensive_language et neither. La première difficulté qu’on remarque rapidement, c’est que les classes ne sont pas équilibrées, donc l’accuracy seule ne suffit pas pour évaluer correctement les performances du modèle.

J’ai donc mis en place un split stratifié avec un random_state fixé à 42 pour garder des résultats reproductibles. Ensuite, j’ai utilisé une vectorisation TF-IDF avec des n-grams de taille 1 à 2, puis comparé deux approches : la régression logistique et la forêt aléatoire.

L’objectif derrière cette partie était de construire une base fiable pour le projet : avoir des données bien préparées, des modèles sauvegardés, des résultats qu’on peut reproduire et surtout une meilleure compréhension des limites du système.
