# Fiche de modèle — AI Content Guardian

## 1. Finalité

Prototype éducatif de modération de contenu textuel (tweets). Objectif : aider un modérateur humain à repérer rapidement du contenu potentiellement problématique. **Jamais** utilisé pour bannir ou supprimer automatiquement sans recours.

## 2. Données

- Fichier : `backend/data/labeled_data.csv` (Hate Speech and Offensive Language Dataset, Davidson et al.).
- Colonnes utilisées : `tweet`, `class` (0=hate speech, 1=offensive language, 2=neither), `count`, `hate_speech`, `offensive_language`, `neither`.
- Taille après nettoyage : 24 783 tweets.
- Distribution :
  - hate_speech : 1 430 (5,8 %)
  - neither : 4 163 (16,8 %)
  - offensive_language : 19 190 (77,4 %)
- Déséquilibre traité par `class_weight='balanced'` et macro-F1.

## 3. Traitement du texte

- Suppression des mentions (`@user`) et URLs.
- Conservation de la casse et de la ponctuation pour l'intensité/sarcasme.
- TF-IDF : 3 000 features, 1-2-grams, `sublinear_tf=True`, lowercasing géré par le vectorizer.
- Traduction automatique vers l'anglais si la langue détectée n'est pas l'anglais.

## 4. Modèles

| Modèle | Type | Intérêt |
|---|---|---|
| `logistic_regression.joblib` | Régression logistique multinomiale sur TF-IDF | Interprétable (coefficients par classe) |
| `random_forest.joblib` | Forêt aléatoire (100 arbres, profondeur max 25) sur TF-IDF | Modèle complexe, explicable par SHAP/LIME |

Split : 80/20 stratifié, `random_state=42`.

## 5. Performances (sur jeu de test)

### Régression logistique
- Accuracy : 0,8400
- Macro-F1 : 0,7058
- hate_speech : P=0,286 / R=0,601 / F1=0,388
- offensive_language : P=0,964 / R=0,841 / F1=0,898
- neither : P=0,760 / R=0,918 / F1=0,832

### Forêt aléatoire
- Accuracy : 0,8322
- Macro-F1 : 0,6895
- hate_speech : P=0,328 / R=0,535 / F1=0,407
- offensive_language : P=0,970 / R=0,833 / F1=0,896
- neither : P=0,649 / R=0,933 / F1=0,766

## 6. Limites connues

- Dataset américain, annoté dans un contexte culturel spécifique ; généralisation limitée.
- Déséquilibre classe ; la classe hate_speech a un rappel faible (~0,5–0,6).
- Le proxy AAE est une approximation lexicale grossière, **pas** un label de dialecte validé. Voir `services/dialect_proxy.py`.
- Risque de faux positifs sur des marqueurs dialectaux, du sarcasme ou des citations.

## 7. Audit équité

Proxy AAE : score lexical 0-1 basé sur 22 marqueurs. Seuil dialectal utilisé pour l'audit : 0,15.

Sur le jeu de test :
- Taux de signalement (hate_speech ou offensive) avec forts marqueurs : 0,8713.
- Taux de signalement avec faibles marqueurs : 0,7757.
- Écart : 0,0956.

Cet écart est un signal de fragilité, pas une preuve démographique directe.

## 8. Supervision humaine et recours

- Le modèle fournit une recommandation et des probabilités.
- Toute action restrictive doit être validée par un humain.
- L'utilisateur doit pouvoir contester une décision et obtenir une explication (mots influents + scores).

## 9. Cadre légal

- Liberté d'expression vs modération légitime.
- RGPD : en production, base légale, information, minimisation des données et droit de recours (art. 22 sur les décisions automatisées).
