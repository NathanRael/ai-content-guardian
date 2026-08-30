# Organisation des rôles du projet

Ce document propose une répartition en cinq rôles complémentaires pour le projet **Gardien de Contenu IA**. Les rôles coopèrent ; chacun est responsable d’une dimension critique du système de modération.

---

## 1. Cadrage et parties prenantes

### Mission
Définir la finalité du produit, identifier les utilisateurs et les personnes affectées, et s’assurer que le système répond à un besoin réel sans créer de dommages prévisibles.

### Responsabilités
- Clarifier l’objectif principal : assistant de modération humain, pas de décision automatique de bannissement.
- Identifier les utilisateurs directs (modérateurs, chercheurs, étudiants) et les personnes affectées (auteurs de contenus analysés).
- Recenser les risques éthiques et juridiques : faux positifs, faux négatifs, liberté d’expression, discrimination.
- Valider les scénarios d’usage et les cas à traiter en priorité.
- Animer la concertation avec les parties prenantes et documenter les choix.

### Livrables attendus
- Fiche de cadrage : finalité, utilisateurs, personnes affectées, risques.
- Scénarios d’usage validés.
- Comptes-rendus de réunions avec parties prenantes.

### Interaction avec les autres rôles
- Alimente le rôle **Données et modèle** avec les besoins métier.
- Valide avec le rôle **Gouvernance, documentation et qualité** que les risques sont traités.

---

## 2. Données et modèle

### Mission
Préparer les données, entraîner et versionner les modèles, et garantir que le pipeline de modération est reproductible.

### Responsabilités
- Nettoyer et documenter le jeu de données (`datasets/labeled_data.csv`).
- Garantir la reproductibilité du split train/test (stratifié, `random_state` fixé, indices sauvegardés).
- Entraîner, comparer et versionner les modèles (régression logistique, forêt aléatoire).
- Vectoriser le texte de manière cohérente entre les modèles.
- Gérer les artefacts : modèles, vectoriseur, métadonnées.

### Livrables attendus
- Jeu de données nettoyé et documenté.
- Modèles entraînés et versionnés dans `backend/models/`.
- Pipeline de split et de vectorisation reproductible.
- Métadonnées des modèles (date, données utilisées, hyperparamètres).

### Interaction avec les autres rôles
- Travaille avec **Évaluation/biais** pour identifier les faiblesses des modèles.
- Fournit à **Explicabilité/interface** les artefacts nécessaires aux explications.
- Documente les limites connues pour **Gouvernance, documentation et qualité**.

---

## 3. Évaluation et biais

### Mission
Mesurer les performances des modèles, détecter les biais et réaliser des stress tests éthiques sur des populations ou des variantes linguistiques sensibles.

### Responsabilités
- Calculer les métriques par classe (précision, rappel, F1) et privilégier la macro-F1 en raison du déséquilibre des classes.
- Produire et analyser les matrices de confusion.
- Concevoir et exécuter un audit de biais (proxy AAE, paires standard/variante, écarts de taux de signalement).
- Identifier et documenter les cas limites.
- Vérifier que les deux modèles partagent le même protocole expérimental.

### Livrables attendus
- Rapport de métriques (`outputs/metrics.json`, matrices de confusion).
- Rapport d’audit de biais (`outputs/audit.json`, `outputs/demo_pairs.csv`).
- Liste des cas limites avec analyse (`outputs/edge_cases.csv`, `outputs/lime_edge_cases.json`).

### Interaction avec les autres rôles
- Signale les biais à **Données et modèle** pour itérer sur les données ou l’entraînement.
- Fournit les résultats d’audit à **Explicabilité/interface** pour les afficher dans l’interface.
- Valide avec **Gouvernance, documentation et qualité** que les risques sont documentés.

---

## 4. Explicabilité et interface

### Mission
Rendre les décisions du modèle compréhensibles pour l’utilisateur final et construire une interface qui accompagne le modérateur humain.

### Responsabilités
- Produire des explications locales (LIME) et globales (SHAP) pour chaque prédiction.
- Concevoir l’interface utilisateur : analyse unitaire, simulation de lots, tableau de bord, audit, fiche modèle.
- Afficher les recommandations en langage clair et jamais comme des décisions définitives.
- Permettre la comparaison des deux modèles et la visualisation des écarts.
- Intégrer les résultats de l’audit de biais de manière transparente.

### Livrables attendus
- Interface Next.js avec toutes les pages fonctionnelles.
- Composants réutilisables : `CommentCard`, `ModelComparisonPanel`, `ExplanationPanel`, `BiasAuditChart`, etc.
- Client API typé et gestion des erreurs en français.
- Explications LIME/SHAP accessibles dans l’interface.

### Interaction avec les autres rôles
- S’appuie sur **Données et modèle** pour les artefacts et prédictions.
- Intègre les résultats de **Évaluation/biais** dans les pages d’audit.
- Respecte les exigences de **Gouvernance, documentation et qualité** en matière de transparence et de droit au recours.

---

## 5. Gouvernance, documentation et qualité

### Mission
Garantir que le projet respecte un cadre éthique, légal et qualitatif, et que toutes les décisions sont traçables et documentées.

### Responsabilités
- Rédiger la fiche modèle (`docs/model_card.md`) et le cadre de gouvernance (`docs/governance.md`).
- S’assurer du respect du RGPD : minimisation, anonymisation possible, information, droit de recours.
- Vérifier que le modèle ne décide jamais seul d’une sanction (humain dans la boucle).
- Définir les processus de revue, de validation et de recours.
- Contrôler la qualité du code, de la documentation et des tests.

### Livrables attendus
- Fiche modèle complète.
- Document de gouvernance.
- Procédures de revue humaine et de recours.
- Rapport de conformité et de qualité.

### Interaction avec les autres rôles
- Valide le cadrage réalisé par **Cadrage et parties prenantes**.
- S’assure que **Données et modèle** et **Évaluation/biais** documentent leurs limites.
- Vérifie que **Explicabilité/interface** communique clairement le rôle humain et les risques.

---

## Schéma de coopération

```
Cadrage/parties prenantes
        |
        v
Données et modèle <--> Évaluation/biais
        |                     |
        v                     v
Explicabilité/interface <-- Gouvernance, documentation et qualité
```

Chaque rôle livre des artefacts tangibles. Les points de blocage remontent au rôle **Gouvernance, documentation et qualité**, qui arbitrage en cas de conflit entre performance, équité et conformité.
