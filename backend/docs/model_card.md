# Fiche de modèle — Détecteur de discours haineux

## 1. Finalité

Prototype éducatif de détection de discours haineux sur des tweets.
Objectif : aider un modérateur humain à repérer rapidement du contenu potentiellement problématique, **jamais** à bannir ou supprimer automatiquement sans recours.

## 2. Données

- Fichier : `datasets/labeled_data.csv` (Hate Speech and Offensive Language Dataset, Davidson et al.).
- Colonnes utilisées : `tweet`, `class` (0=hate speech, 1=offensive language, 2=neither), `count`, `hate_speech`, `offensive_language`, `neither`.
- Taille : 24 783 tweets après nettoyage.
- Distribution des classes :
  - hate_speech : 1 430 (5,8 %)
  - neither : 4 163 (16,8 %)
  - offensive_language : 19 190 (77,4 %)
- Déséquilibre marqué, pris en compte par `class_weight='balanced'` et par le choix de la macro-F1.

## 3. Traitement du texte

- Suppression des mentions (`@user`) et des URLs.
- Conservation de la ponctuation et de la casse (elles peuvent porter de l'intensité).
- Retrait des caractères spéciaux inutiles.
- TF-IDF : 3 000 features, bigrammes 1-2, `sublinear_tf=True`.

## 4. Modèles

| Modèle | Type | Intérêt |
|---|---|---|
| `logistic_regression.joblib` | Régression logistique multinomiale sur TF-IDF | Interprétable (coefficients par classe) |
| `random_forest.joblib` | Forêt aléatoire (100 arbres, profondeur max 25) sur TF-IDF | Modèle complexe, explicable par SHAP/LIME |

Le proxy dialectal AAE **n'est pas** une feature d'entraînement.

## 5. Performances (split 80/20 stratifié, random_state=42)

Source : `outputs/metrics.json`

### Régression logistique
- Accuracy : 0,8396
- Macro-F1 : 0,7056
- hate_speech : P=0,286 / R=0,605 / F1=0,388
- offensive_language : P=0,964 / R=0,841 / F1=0,898
- neither : P=0,760 / R=0,916 / F1=0,831

### Forêt aléatoire
- Accuracy : 0,8346
- Macro-F1 : 0,6919
- hate_speech : P=0,332 / R=0,542 / F1=0,412
- offensive_language : P=0,968 / R=0,838 / F1=0,898
- neither : P=0,656 / R=0,921 / F1=0,766

## 6. Limites connues

- Dataset américain, annoté dans un contexte culturel spécifique ; généralisation limitée.
- Déséquilibre classe ; la classe hate_speech a un rappel faible (~0,5–0,6).
- Le proxy AAE est une approximation lexicale grossière, **pas** un label de dialecte validé. Voir `src/hate_speech_detector/data.py`.
- Risque de faux positifs sur des marqueurs dialectaux ou des citations.

## 7. Stress test équité

Source : `outputs/audit.json`

Sur le jeu de test, parmi les tweets réellement neutres (`class=2`) :
- AAE proxy élevé : 9,3 % classés « offensive_language » par LR.
- AAE proxy faible : 3,8 % classés « offensive_language » par LR.

Écart notable, à interpréter comme un signal de fragilité, pas comme un audit démographique direct.

## 8. Supervision humaine et recours

- Le modèle fournit une recommandation et une probabilité.
- Toute action restrictive (suppression, bannissement) doit être validée par un humain.
- L'utilisateur doit pouvoir contester une décision et obtenir une explication (probabilités + mots influents).

## 9. Cadre légal

- Liberté d'expression vs modération légitime (p.ex. CDA Section 230 aux États-Unis, jurisprudences européennes sur la modération).
- RGPD : si des données utilisateur sont traitées en production, il faut une base légale, l'information des personnes, la minimisation des données et un droit de recours (art. 22 sur les décisions automatisées).
