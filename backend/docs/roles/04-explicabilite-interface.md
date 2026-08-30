# 4. Explicabilité et interface

## Ce qu'il faut savoir

Un bon outil de modération ne doit pas seulement prédire. Il doit expliquer. C'est le cœur de la confiance, et c'est ce qui évite qu'un système soit utilisé comme boîte noire.

Le backend fournit des explications locales et globales :

- LIME pour les prédictions individuelles ;
- SHAP global pour l'importance des traits sur l'ensemble du jeu de test ;
- probabilités par classe et mots influents dans les résultats d'analyse.

Dans le code, `backend/services/explainability.py` et `backend/routers/analyze.py` donnent les éléments nécessaires pour expliquer une décision. Le front-end est conçu pour afficher ces éléments de manière lisible et en français.

L'interface ne doit pas présenter une prédiction comme une vérité absolue. Elle doit présenter une recommandation, une explication et un contexte. C'est un point crucial dans le projet, parce que le but est d'aider un modérateur, pas de sanctionner sans contrôle humain.

## Ce que le backend confirme

- `backend/routers/model_info.py` retourne les features SHAP globales.
- `backend/services/recommendation.py` gère les recommandations utilisateur.
- `backend/main.py` centralise l'API et les endpoints d'analyse.
- `README.md` précise que tous les textes affichés doivent être en français.

## Points de vigilance

- Les termes mis en avant doivent être compréhensibles par un modérateur, pas seulement par un data scientist.
- L'interface doit montrer les limites du modèle.
- La comparaison entre modèles doit être claire, notamment pour les cas douteux.
- L'outil ne doit jamais masquer le rôle de l'humain dans la décision finale.

## Discours d'une minute
De mon côté, j’ai travaillé sur la partie explicabilité et interface, avec l’objectif de rendre les résultats du modèle plus faciles à comprendre pour la personne qui va les utiliser.

Concrètement, je me suis concentré sur le fait de ne pas afficher seulement une prédiction, mais aussi les éléments qui permettent de l’interpréter. Pour chaque résultat, on retrouve les mots qui ont influencé le score, les probabilités associées aux différentes classes, ainsi que des explications basées sur LIME et SHAP.

L’objectif était d’éviter l’effet "boîte noire". Un modérateur doit pouvoir comprendre pourquoi un message est signalé avant de prendre une décision. L’interface doit donc aider à analyser la situation, surtout pour les cas où la prédiction n’est pas évidente.

Ce qu’il faut retenir, c’est que le modèle reste un outil d’aide à la décision. Il donne des informations et des explications, mais il ne remplace pas le jugement humain. Mon rôle était donc de faire en sorte que le système accompagne l’utilisateur au lieu de décider à sa place.
