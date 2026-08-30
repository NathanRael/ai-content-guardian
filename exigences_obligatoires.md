# Exigences obligatoires — preuves backend

Ce document mappe les 5 exigences obligatoires du sujet vers les fichiers, endpoints et chiffres concrets du backend. Les points qui nécessitent aussi une preuve frontend sont signalés explicitement.

---

## 1. Finalité, utilisateurs, personnes affectées, données, hypothèses, erreurs et conséquences

- **Finalité** : prototype de modération assistée de contenus textuels (tweets). Le backend aide un modérateur humain, ne décide jamais seul de sanctionner.
- **Utilisateurs** : modérateurs, chercheurs, étudiants.
- **Personnes affectées** : auteurs des contenus analysés.
- **Données** : `backend/data/labeled_data.csv` (Davidson et al.). Colonnes utilisées : `tweet`, `class`, `count`, `hate_speech`, `offensive_language`, `neither`.

Taille et distribution (après nettoyage) dans `backend/outputs/class_distribution.csv` :

| Classe | Effectif | Part |
|---|---|---|
| hate_speech | 1 430 | 5,8 % |
| neither | 4 163 | 16,8 % |
| offensive_language | 19 190 | 77,4 % |

Le fort déséquilibre motive `class_weight='balanced'` et l'utilisation de la macro-F1. Source : `services/ml_pipeline.py`, `train.py`.

Risques documentés dans `model_card.md` et `GET /model-info` :
- Faux positif → sanction injustifiée, atteinte à la liberté d'expression.
- Faux négatif → contenu nuisible non détecté.
- Biais dialectal possible sur le proxy AAE.

**Preuve frontend attendue** : l'interface doit afficher la fiche de modèle, l'avertissement "outil d'aide à la décision" et un bouton de contestation/recours.

---

## 2. Comparaison des deux modèles

Mêmes conditions : split 80/20 stratifié, `random_state=42`, TF-IDF 3 000 features, 1-2-grams, entraînés dans `train.py`.

Résultats complets dans `backend/outputs/metrics.json` et exposés via `GET /metrics` :

| Modèle | Accuracy | Macro-F1 | hate_speech F1 | offensive F1 | neither F1 |
|---|---|---|---|---|---|
| Régression logistique | 0,8400 | 0,7058 | 0,3878 | 0,8980 | 0,8315 |
| Forêt aléatoire | 0,8322 | 0,6895 | 0,4069 | 0,8960 | 0,7655 |

Matrices de confusion incluses dans la réponse `/metrics`.

**Preuve frontend attendue** : affichage comparatif LR vs RF, matrices de confusion, graphiques de performance.

---

## 3. Protocole reproductible

- Split stratifié 80/20 avec `random_state=42` : `services/ml_pipeline.py`, fonction `train_and_save()`.
- Indices sauvegardés : `backend/outputs/idx_train.joblib`, `backend/outputs/idx_test.joblib`.
- Métriques par classe (précision, rappel, F1) et accuracy dans `outputs/metrics.json`.
- Macro-F1 utilisée comme métrique principale pour compenser le déséquilibre.

Trois cas limites documentés dans `backend/outputs/edge_cases.json` et exposés via `/metrics` :

| Cas | Texte | LR | RF | Note |
|---|---|---|---|---|
| Sarcasme | "Oh great, another genius opinion..." | neutral (0,69) | neutral (0,42) | Le mépris masqué peut être classé à tort comme neutre. |
| Insulte objet | "This printer is a stupid piece of junk." | hate_speech (0,49) | neutral (0,43) | Mots offensants sans cible humaine. |
| Variante dialectale | "Imma be real witchu, that movie ain't it." | offensive (0,52) | offensive (0,37) | Marqueurs AAE → surestimation de toxicité. |

**Preuve frontend attendue** : visualisation des cas limites et de leurs explications LIME.

---

## 4. Audit de biais / stress test éthique

Proxy AAE : liste de 22 marqueurs lexicaux et morpho-syntaxiques dans `services/dialect_proxy.py`. **Jamais utilisée comme feature d'entraînement**. Méthodologie en français dans la réponse `GET /bias-audit`.

Résultats calculés sur le jeu de test (seuil de score dialectal = 0,15) :

| Groupe | Taux de signalement (LR + RF moyenne) |
|---|---|
| Forts marqueurs dialectaux | 0,8713 |
| Faibles marqueurs dialectaux | 0,7757 |
| **Écart** | **0,0956** |

Paires d'exemples standard / variante dialectale incluses dans `/bias-audit` :
- "I am going to the store right now." → LR neutral / "Imma run to the store right quick." → LR offensive.
- "I do not want to do this homework." → LR neutral / "I ain't tryna do this homework tho." → LR offensive.

Source : `train.py` (fonction `build_bias_audit`) + `services/dialect_proxy.py`.

**Preuve frontend attendue** : affichage de l'écart de signalement et des paires d'exemples.

---

## 5. Explicabilité et gouvernance

- **LIME** : explications locales par texte pour `/analyze-comment` (`services/explainability.py`, `routers/analyze.py`).
- **SHAP global** : `services/explainability.py` + `train.py`, résultat dans `backend/outputs/shap_global.json`, exposé via `GET /model-info` (`global_shap_features`).
- **Gouvernance** : `GET /model-info` retourne `intended_use`, `not_intended_for`, `known_limitations`, `human_role`. Aucune décision automatique de suppression/bannissement n'est prévue.
- **Messages utilisateur en français** : `services/recommendation.py` (raisons de recommandation), gestion des erreurs dans les routers.

**Preuve frontend attendue** :
- Affichage des mots LIME pour chaque analyse.
- Affichage des features SHAP globales.
- Parcours de contestation / recours utilisateur.

---

## Récapitulatif des fichiers clés

| Fichier | Rôle |
|---|---|
| `backend/main.py` | FastAPI, CORS, gestion des erreurs |
| `backend/routers/*.py` | Endpoints |
| `backend/services/*.py` | Logique métier |
| `backend/train.py` | Entraînement + génération des artefacts |
| `backend/outputs/metrics.json` | Métriques des modèles |
| `backend/outputs/edge_cases.json` | Cas limites |
| `backend/outputs/bias_audit.json` | Audit de biais |
| `backend/outputs/shap_global.json` | Importance globale SHAP |
| `backend/models/*.joblib` | Modèles persistés |
| `model_card.md` | Fiche modèle pour l'annexe |
