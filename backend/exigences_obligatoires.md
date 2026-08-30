# Exigences obligatoires, preuves concrètes

J'ai regroupé ici les preuves pour chacune des 5 exigences. Chaque section pointe vers le fichier et le résultat exact.

## 1. Finalité, utilisateurs, personnes affectées, données, hypothèses, erreurs et conséquences

Le projet est un prototype de détection de discours haineux sur tweets. Il aide un modérateur humain. Il ne décide jamais seul de bannir ou de supprimer. Les utilisateurs visés sont des modérateurs, des chercheurs et des étudiants. Les personnes affectées sont les auteurs des contenus analysés. Si le modèle est utilisé seul, elles risquent une sanction injustifiée.

Les données viennent de `datasets/labeled_data.csv`. Après nettoyage, le fichier contient 24 783 tweets. Les colonnes utilisées sont `tweet`, `class`, `count`, `hate_speech`, `offensive_language` et `neither`.

La répartition des classes, dans `outputs/class_distribution.csv`, est inégale.

| Classe | Effectif | Part |
|---|---|---|
| hate_speech | 1 430 | 5,8 % |
| neither | 4 163 | 16,8 % |
| offensive_language | 19 190 | 77,4 % |

Cette dominance de `offensive_language` justifie `class_weight='balanced'` et le choix de la macro-F1. Le code est dans `src/hate_speech_detector/data.py`.

Hypothèses et risques :
- Les marqueurs AAE sont rares dans le dataset. Le modèle peut les confondre avec de la toxicité.
- Un faux positif expose l'auteur à une sanction injustifiée et touche à la liberté d'expression.
- Un faux négatif laisse passer un contenu nuisant.

Ces points sont développés dans `docs/model_card.md` et `docs/governance.md`.

## 2. Comparaison des deux modèles

Les deux modèles partagent exactement le même split 80/20 stratifié sur `class`, avec `random_state=42`, et la même vectorisation TF-IDF à 3 000 features et 1-2-grams. Les résultats sont dans `outputs/metrics.json`.

| Modèle | Accuracy | Macro-F1 | hate_speech F1 | offensive_language F1 | neither F1 |
|---|---|---|---|---|---|
| Régression logistique | 0,8396 | 0,7056 | 0,3883 | 0,8979 | 0,8307 |
| Forêt aléatoire | 0,8346 | 0,6919 | 0,4117 | 0,8983 | 0,7659 |

La régression logistique gagne sur la macro-F1, surtout grâce à `neither`. La forêt aléatoire fait un peu mieux sur `hate_speech` mais confond plus `neither`. Les deux modèles mélangent `hate_speech` et `offensive_language`. Cela reflète la façon dont le dataset a été annoté.

Les matrices de confusion, l'importance SHAP et les summary plots sont dans `outputs/`.

## 3. Protocole reproductible

Le split est fait avec `train_test_split(..., test_size=0.2, random_state=42, stratify=df['class'])`. Les indices sont sauvegardés dans `outputs/idx_train.joblib` et `outputs/idx_test.joblib`. Le code est dans `src/hate_speech_detector/data.py`, fonction `split_data`.

Accuracy est calculée mais elle pèse peu la classe minoritaire. C'est pourquoi on rapporte aussi precision, recall et F1 par classe. La macro-F1 est la métrique principale. Elle moyenne chaque classe sans tenir compte de son effectif. Le calcul est dans `src/hate_speech_detector/evaluate.py`.

Matrice de confusion de la régression logistique, tirée de `outputs/confusion_matrix_logistic_regression.csv`.

| Vrai \ Prédit | hate_speech | offensive_language | neither |
|---|---|---|---|
| hate_speech | 173 | 86 | 27 |
| offensive_language | 398 | 3226 | 214 |
| neither | 34 | 36 | 763 |

### Trois cas limites

Ces exemples viennent de `outputs/edge_cases.csv` et `outputs/lime_edge_cases.json`.

**Faux positif avec marqueurs AAE, RF.** Le tweet "RT : If you ain't a gator you're gator bait 128076;" est annoté `neither`. La forêt aléatoire le classe `hate_speech` avec une probabilité de 0,3955. Le modèle associe "ain't" et le contexte à de la toxicité. LIME/SHAP pointent "you", "re" et "ain".

**Discours haineux correctement détecté, RF.** Le tweet "@Brizgotti These new nigga hipster hypebeasts love all these faggot ass bright colors and Nike keeps giving them what they want smh" est annoté `hate_speech` et prédit `hate_speech` avec 0,577. Les termes injurieux "faggot", "ass" et "nigga" dominent l'explication.

**Frontière offensive / neither, RF.** Le tweet "@MakEitSndGoOd @Fewjr we block us then and see what happens. You think we on ya high yellow ass now. Just watch" est annoté `offensive_language` mais prédit `neither` avec 0,4211. Le modèle hésite car il n'y a pas de terme injurieux explicite. LIME/SHAP retiennent "yellow" et "ass".

## 4. Audit de biais / stress test éthique

Le proxy AAE n'est pas un label de dialecte. C'est une liste de 23 marqueurs lexicaux et constructions grammaticales : "finna", "tryna", "ain't", "y'all", le "be" habituel, le "done" complétif, la négation multiple, etc. Pour chaque tweet, on compte les marqueurs et on normalise par la longueur du tweet. Ce proxy n'est jamais une feature d'entraînement. C'est une approximation grossière, documentée comme telle, inspirée de Blodgett et al. (2016). Le code est dans `src/hate_speech_detector/data.py` et `src/hate_speech_detector/audit.py`.

Résultats du stress test, dans `outputs/audit.json`.

| Groupe | n | LR % hate prédit | LR % offensive prédit |
|---|---|---|---|
| AAE proxy élevé | 874 | 9,4 % | 80,1 % |
| AAE proxy faible | 4 083 | 12,8 % | 64,9 % |
| Neutre + AAE élevé | 75 | 6,7 % | 9,3 % |
| Neutre + AAE faible | 758 | 3,8 % | 3,8 % |

Le chiffre qui inquiète est le dernier. Parmi les tweets réellement neutres, le modèle de régression logistique classe 9,3 % des tweets à marqueurs AAE comme `offensive_language`, contre 3,8 % pour les tweets sans marqueur. C'est un écart de 2,5 points à contenu comparable. Cela ne prouve pas une discrimination démographique directe. Le proxy ne capture pas la grammaire complète, le contexte ou l'identité réelle de l'auteur. Mais il montre que le modèle est moins fiable sur certaines variantes linguistiques.

`outputs/demo_pairs.csv` contient des paires SAE/AAE de même sens. Par exemple, "I am going to the store right now." est prédit `neither`, alors que "Imma run to the store right quick." est prédit `offensive_language` par la régression logistique.

## 5. Explicabilité et gouvernance

LIME donne une explication textuelle par cas limite. SHAP calcule les valeurs de Shapley sur la forêt aléatoire, individuellement et globalement. Le dashboard Streamlit affiche les mots les plus influents pour chaque prédiction. Les fichiers sont `src/hate_speech_detector/explain.py`, `outputs/lime_edge_cases.json`, `outputs/shap_importance.csv` et `outputs/shap_summary_hate_speech.png`.

`outputs/shap_importance.csv` classe les mots et bigrammes par importance moyenne pour chaque classe. Les summary plots montrent quels termes poussent vers `hate_speech` ou `offensive_language`.

Sur la gouvernance, le modèle ne bannit ni ne supprime jamais automatiquement. Un modérateur humain valide chaque action. L'utilisateur peut demander une revue. La décision est motivée. En production, le traitement des données utilisateur doit respecter la minimisation, l'anonymisation possible, l'information des personnes et le droit de recours de l'article 22 du RGPD. La fiche de modèle est dans `docs/model_card.md`. Le cadre légal est traité dans `docs/governance.md` et le dashboard dans `src/hate_speech_detector/dashboard.py`.

---

## Preuves côté frontend

Les pages et composants suivants démontrent que les exigences sont respectées dans l'interface.

### 1. Finalité, utilisateurs, personnes affectées, données, hypothèses, erreurs et conséquences

- Page **Fiche modèle** (`/fiche-modele`) : affiche `intended_use`, `not_intended_for`, `known_limitations`, `human_role` et le résumé des données d'entraînement renvoyés par `GET /model-info`.
- Page **Audit** (`/audit`) : la `methodology_note` de `GET /bias-audit` est affichée en premier, dans un encart dédié, avec l'icône `Scale`.
- Composant `RecommendationBanner` : rappelle explicitement quand un "revu humain recommandé" est nécessaire, sans décision automatique de bannissement.

### 2. Comparaison des deux modèles

- Composant `ModelComparisonPanel` (page **Analyser** `/analyser` et détail de chaque `CommentCard`) : affiche côte à côte les prédictions de la régression logistique et de la forêt aléatoire avec leur confiance et l'indicateur "Les modèles sont d'accord / ne sont pas d'accord".
- Page **Audit** (`/audit`) : matrices de confusion des deux modèles sous forme de tableaux heatmap, alimentées par `GET /metrics`.

### 3. Protocole reproductible et cas limites

- Page **Audit** (`/audit`) : les trois cas limites renvoyés par `GET /metrics` (`edge_cases`) sont listés avec leur texte, leur prédiction et leur note.
- Les matrices de confusion de la page **Audit** matérialisent le protocole d'évaluation (mêmes splits et métriques que le backend).

### 4. Audit de biais / stress test éthique

- Page **Audit** (`/audit`) :
  - `BiasAuditChart` : comparaison visuelle des taux de signalement entre les contenus à marqueurs AAE élevés et faibles, avec l'écart numérique.
  - Liste des `example_pairs` (version standard vs variante de dialecte) avec les prédictions des deux modèles.
  - La `methodology_note` est affichée en premier pour expliquer le proxy AAE et ses limites.

### 5. Explicabilité et gouvernance

- Composant `ExplanationPanel` (page **Analyser** `/analyser` et détail de chaque `CommentCard`) : affiche les poids LIME sous forme de diagramme en barres horizontales, avec une explication du rôle des poids positifs / négatifs, et l'indicateur du score de marqueurs de dialecte.
- Page **Fiche modèle** (`/fiche-modele`) : section "Rôle humain" et "Usage non prévu" pour rappeler le cadre de gouvernance.
- Composant `RecommendationBanner` : affiche la raison de la recommandation en langage clair, à destination du modérateur humain.
