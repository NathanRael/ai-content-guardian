# 3. Évaluation et biais

## Ce qu'il faut savoir

L'évaluation du projet ne se limite pas à dire que le modèle est bon ou mauvais. Il faut mesurer la performance par classe, regarder les erreurs, et tester les situations sensibles.

Le projet compare deux modèles sur les mêmes bases :

- régression logistique ;
- forêt aléatoire.

Les résultats montrent une performance globale correcte, mais pas impeccable. La régression logistique est légèrement meilleure sur la macro-F1 et sur l'ensemble des métriques globales. Cela est documenté dans `backend/outputs/metrics.json` et exposé par `backend/routers/metrics.py`.

Le projet avance aussi un audit de biais. Il ne construit pas un classifieur de dialecte, mais il utilise un proxy lexical AAE pour mesurer si des textes avec des marqueurs dialectaux sont plus souvent signalés. Le score gap documenté est de 0,0956 : les textes à fort marqueur dialectal sont plus souvent classés comme problématiques que les autres.

## Ce que le backend confirme

- `backend/train.py` construit les métriques, les matrices de confusion et les cas limites.
- `backend/services/dialect_proxy.py` calcule le score de marqueur dialectal.
- `backend/outputs/edge_cases.json` réunit les cas limites comme le sarcasme et les variantes dialectales.
- `backend/routers/audit.py` et `backend/routers/metrics.py` exposent ces résultats.

## Points de vigilance

- Le proxy AAE est une approximation ; il ne doit pas être confondu avec une mesure de dialecte réel.
- Les faux positifs peuvent être renforcés sur des textes de style informel ou dialectal.
- Les cas limites doivent être utilisés pour corriger l'outil, pas pour le présenter comme fiable en l'état.
- L'évaluation doit rester centrée sur l'usage humain et le risque de sanction injustifiée.

## Discours d'une minute

De mon côté, je me suis occupé de l’évaluation du modèle, avec un objectif simple : vérifier qu’il fonctionne correctement, mais aussi qu’il reste juste dans ses décisions.

J’ai donc analysé les performances par classe, les matrices de confusion et certains cas où le modèle peut se tromper. On compare notamment la régression logistique et la forêt aléatoire sur le même jeu de test, mais il ne faut pas s’arrêter uniquement à l’accuracy. La macro-F1 est plus intéressante ici, car elle permet de voir si le modèle traite correctement toutes les classes, même celles qui sont moins représentées.

J’ai aussi réalisé un audit de biais avec un proxy AAE pour vérifier si certains textes contenant des marqueurs dialectaux étaient plus souvent signalés comme offensifs. Il faut être précis sur l’interprétation : ce résultat ne prouve pas une discrimination directe, mais il montre un risque potentiel que le modèle doit prendre en compte.

Mon rôle était donc de montrer qu’un bon modèle ne se juge pas seulement par ses scores de performance. Il faut aussi regarder sa robustesse, ses limites et les situations dans lesquelles il peut prendre de mauvaises décisions.
