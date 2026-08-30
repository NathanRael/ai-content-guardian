# Gouvernance du détecteur de discours haineux

Ce document décrit les règles d'utilisation, de contrôle et de recours autour du modèle.

## Ce que le modèle fait

Le classifieur prend un tweet en entrée et renvoie une probabilité sur trois classes : discours haineux, langage offensant, ou ni l'un ni l'autre. Il repose sur un vecteur TF-IDF et sur deux modèles entraînés : une régression logistique multinomiale et une forêt aléatoire. Le proxy AAE n'est pas une entrée du modèle. Il sert uniquement à l'audit après la prédiction.

## Supervision humaine obligatoire

Le modèle ne supprime, ne bannit et ne sanctionne pas seul. Il signale. Le workflow de modération est le suivant.

1. Le modèle fournit une classe prédite, un score de confiance et les mots les plus influents.
2. Un modérateur humain relit le texte, son contexte et l'explication.
3. Le modérateur prend la décision finale.
4. L'utilisateur peut contester. La décision finale doit être motivée et réversible.

## Recours et transparence

L'utilisateur reçoit la classe prédite, les probabilités par classe et les termes qui ont le plus pesé. Il peut demander une revue humaine. Les logs de décision sont conservés pour auditer les erreurs systémiques.

## Données personnelles et RGPD

Si le modèle traite des données utilisateur en production, les exigences suivantes s'appliquent.

- Base légale : identifier un intérêt légitime ou une obligation contractuelle avant tout traitement.
- Minimisation : ne conserver les textes que le temps nécessaire à la modération.
- Anonymisation : dissocier les textes des identifiants dès que possible.
- Information : informer l'utilisateur du traitement automatisé.
- Droit de recours : prévoir une procédure d'opposition et de contestation, notamment au titre de l'article 22 du RGPD.

## Stress test dialectal

Le proxy AAE est une liste de marqueurs lexicaux simples. Il ne remplace pas une identification linguistique rigoureuse. Il mesure si des tournures associées à l'AAE augmentent le risque de faux positif. C'est un test de fragilité, pas un audit démographique.

Référence méthodologique : Blodgett et al. (2016).

## Limites à garder en tête

- Le modèle confond parfois dialecte et toxicité.
- Les traductions automatiques dénaturent le sens.
- Le rappel sur la classe hate_speech reste faible. Le modèle ne peut pas être déployé seul en production.
