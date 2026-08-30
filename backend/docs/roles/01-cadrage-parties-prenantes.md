# 1. Cadrage et parties prenantes

## Ce qu'il faut savoir

Ce projet ne vise pas à remplacer le jugement humain. Il propose un outil d'aide à la modération de contenus textuels, surtout des tweets, pour aider un modérateur à repérer rapidement des messages potentiellement problématiques. La logique est claire dans le backend FastAPI, dans `backend/main.py` et dans la fiche modèle `backend/docs/model_card.md` : le système signale, il n'impose pas de sanction.

Les parties prenantes sont assez simples à identifier :

- les modérateurs qui utilisent l'outil au quotidien ;
- les chercheurs et étudiants qui testent les performances et les biais ;
- les auteurs de contenus analysés, qui peuvent être affectés par un faux positif ;
- les équipes qui doivent garantir l'usage responsable du système.

Les risques sont bien connus dans le projet :

- faux positif : un message sain est jugé problématique ;
- faux négatif : un message nuisible passe sans alerte ;
- risque de discrimination sur des variantes dialectales ;
- risque de confondre langue, style ou tonalité avec toxicité.

Le projet le dit explicitement : l'usage prévu est l'aide à la décision, jamais la décision automatique de bannissement ou de suppression.

## Ce que le backend confirme

- `backend/routers/model_info.py` retourne une description de l'usage prévu et des limites connues.
- `backend/main.py` expose l'API de modération sans logique de sanction automatique.
- `README.md` et `backend/docs/governance.md` soulignent que le rôle humain reste central.

## Points de vigilance

- Le système doit rester un outil de support, pas un juge.
- Il faut définir clairement les cas de recours et les scénarios d'usage.
- Les décisions ne peuvent pas être validées uniquement par un score.
- Le cadre éthique doit être pris au sérieux dès le début.

## Discours d'une minute

Dans ce projet, mon rôle était surtout de définir le cadre autour du système. J’ai travaillé sur sa finalité, sur les personnes qui vont l’utiliser, mais aussi sur celles qui peuvent être impactées par ses décisions.

L’idée principale était de bien préciser que l’outil n’est pas là pour sanctionner automatiquement des personnes. Il sert plutôt à aider les modérateurs dans leur travail. J’ai aussi pris en compte les différents risques, comme les faux positifs, les faux négatifs et les biais liés à la langue, notamment avec les différences de dialectes.

Ce qu’il faut retenir, c’est que le modèle ne prend jamais la décision finale. Il fournit une analyse et des indications, mais c’est toujours un humain qui valide la décision. Mon objectif était donc de m’assurer que le projet garde une approche responsable, parce qu’un outil comme celui-ci peut avoir un impact réel sur les utilisateurs.
