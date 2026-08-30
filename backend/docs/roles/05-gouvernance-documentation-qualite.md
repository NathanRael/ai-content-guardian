# 5. Gouvernance, documentation et qualité

## Ce qu'il faut savoir

La gouvernance ne fait pas que de la paperasse. Elle fixe les règles de bon usage, la traçabilité, le droit de recours et les limites de l'outil. Sans cela, un modèle d'IA peut être utilisé trop loin de son cadre de validité.

Le projet a déjà mis en place les éléments clés :

- fiche modèle ;
- document de gouvernance ;
- réponses explicites sur l'usage prévu et les usages interdits ;
- supervision humaine obligatoire ;
- possibilité de contestation et de revue humaine.

Le backend, via `backend/routers/model_info.py`, précise que le système est un outil d'aide à la modération. Il exclut explicitement la modération entièrement automatique, le déploiement sans supervision, et le traitement des dialectes comme une vérité démographique.

## Ce que le backend confirme

- `backend/docs/governance.md` définit les règles de supervision et de recours.
- `backend/docs/model_card.md` décrit la finalité, les données, les limites et le cadre éthique.
- `backend/routers/model_info.py` fournit les champs `intended_use`, `not_intended_for`, `known_limitations` et `human_role`.
- `backend/main.py` et le code API assurent la gestion standard des erreurs et l'exposition des services.

## Points de vigilance

- Les données doivent rester minimisées et maîtrisées.
- Les décisions de modération doivent toujours être revues par un humain.
- La documentation doit accompagner le développement, pas venir après coup.
- Il faut garder un registre de limites, de tests et d'erreurs connus.

## Discours d'une minute

Pour ma part, je me suis occupé de la partie gouvernance et documentation, avec l’objectif de définir les règles qui encadrent l’utilisation du système.

Concrètement, j’ai travaillé sur la fiche modèle, les limites connues, le rôle de l’humain dans le processus et les solutions possibles en cas de désaccord avec une décision du système. L’idée était de rappeler qu’un outil de modération ne se résume pas à ses performances techniques. Il faut aussi savoir pourquoi il est utilisé, quelles sont ses limites et surtout qui garde la responsabilité de la décision finale.

J’ai donc insisté sur un point important : le modèle peut aider à identifier des contenus, mais il ne doit jamais sanctionner seul ni remplacer le jugement humain.

Au final, la documentation permet de garder une trace claire du fonctionnement du système, de ses risques et de ses limites. Mon rôle était donc de m’assurer que le projet reste encadré, avec une utilisation responsable et une supervision humaine présente.
