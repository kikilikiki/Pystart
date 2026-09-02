# Mode professeur

Le mode professeur permet de creer des cours et des exercices, puis de les
partager avec une classe. Tout se fait **en local** ; aucun serveur.

## Creer un cours

Menu **Professeur > Nouveau cours...**. Pystart cree un dossier pret a editer
dans `%APPDATA%\Pystart\courses\` avec :

- `course.json` (metadonnees a completer) ;
- `lessons/01_introduction.md` (exemple) ;
- `exercises/01_premier_exercice.json` (exemple complet).

Edite ces fichiers (dans l'app ou avec ton editeur habituel). Le format est
decrit dans [courses.md](courses.md) et [exercises.md](exercises.md).

## Modifier / organiser

- L'ordre des lecons et exercices suit le nom de fichier : `01_`, `02_`...
- Le champ `order` de `course.json` place le cours dans la liste.
- Menu **Professeur > Ouvrir le dossier des cours** pour acceder aux fichiers.

## Tests automatiques, indices, solution

Dans chaque exercice JSON :

- `checks` : la liste des verifications (voir [exercises.md](exercises.md)).
- `hints` : autant d'indices que tu veux, du plus vague au plus precis.
- `solution` : le code complet ; l'eleve ne le voit que s'il clique
  explicitement sur « Voir la solution ».

## Exporter un cours

Menu **Professeur > Exporter un cours...** (le cours selectionne dans l'arbre).
Pystart produit une archive **`mon_cours.pystart`** (un ZIP) contenant
`course.json`, `lessons/`, `exercises/` et `assets/`.

## Importer un cours

Menu **Professeur > Importer un cours (.pystart)...**. Pystart :

1. ouvre l'archive **sans rien extraire** et affiche un apercu (titre, niveau,
   nombre de lecons et d'exercices) ;
2. verifie l'archive (voir « Securite » ci-dessous) ;
3. n'ecrit sur le disque qu'apres ta confirmation.

## Partager avec les eleves

Envoie simplement le fichier `.pystart` (mail, cle USB, espace de classe).
Chaque eleve fait **Professeur > Importer**. Le cours apparait alors dans sa
liste, a cote des cours officiels.

## Securite : on ne fait pas confiance aux fichiers importes

Un cours importe est du contenu exterieur. Avant tout import, Pystart refuse :

- les chemins absolus ou contenant `..` (protection *path traversal*) ;
- les fichiers dont l'extension n'est pas autorisee
  (`.json`, `.md`, `.txt`, images) — **aucun `.py` n'est extrait ni execute** ;
- les archives dont le contenu decompresse depasse 50 Mo (*zip bomb*) ;
- les archives sans `course.json`.

Les scripts des exercices restent, eux, executes dans un processus separe avec
timeout (voir [execution.md](execution.md)).
