# Pystart

**Pystart** est une application desktop **gratuite** pour **apprendre Python en
pratiquant**. Les cours, les exemples, les exercices, l'editeur, le terminal et
la verification automatique sont reunis dans une seule fenetre.

L'objectif : passer de _« je ne connais rien a Python »_ a _« je sais creer mes
propres programmes Python »_.

> Statut : version **0.0.1** — premiere version fonctionnelle.

---

## Objectif

- **Pour une personne seule** : apprendre les bases, ecrire et executer du code,
  faire des exercices avec indices et corrections, suivre sa progression, puis
  creer ses propres programmes.
- **Pour un professeur** : creer des cours et des exercices, definir des tests
  automatiques, ajouter indices et solutions, exporter/importer un cours et le
  partager avec sa classe.

Tout fonctionne **en local et hors ligne**. Aucun compte n'est requis.

## Fonctionnalites

| Domaine | Ce que fait Pystart |
|---|---|
| Cours | 16 cours (Hello World -> mini-projets), stockes dans des fichiers, pas dans le code |
| Parcours | Explication -> Exemple -> Exercice -> Indice -> Correction -> Exercice difficile -> Mini-projet |
| Editeur | Coloration Python, numeros de lignes, auto-indentation, thèmes clair/sombre |
| Terminal | stdout, stderr, tracebacks, reponse a `input()` |
| Execution | Processus separe, timeout, bouton Stop, sortie bornee |
| Exercices | 6 types + verification automatique + explications d'erreurs en francais |
| Progression | SQLite : profils, exercices reussis, cours termines, statistiques |
| Professeur | Creation de cours, export/import `.pystart` (ZIP) verifie |
| Bibliotheques | `pip install` dans un environnement virtuel isole |
| Mises a jour | Detection via GitHub Releases, telechargement verifie, updater separe |

## Captures d'ecran

_A venir (dossier `assets/screenshots/`)._

## Installation

### Option recommandee : `Pystart.bat` (sans droits admin, sans alerte antivirus)

Aucun executable compile, aucun installeur : ce lanceur reste dans son
dossier et utilise ton propre Python.

1. Telecharge `Pystart-Portable-X.Y.Z.zip` depuis la page
   [Releases](https://github.com/kikilikiki/Pystart/releases) et decompresse-le
   (ou clone/telecharge le depot entier : `Pystart.bat` est a la racine).
2. Double-clique sur **`Pystart.bat`**.
   - Premier lancement : le script installe automatiquement les
     dependances dans un environnement local (`.pystart-venv`, ~1-2 min,
     connexion Internet necessaire), puis ouvre Pystart.
   - Lancements suivants : demarrage direct.
3. Si Python n'est pas installe, le script te redirige vers
   https://www.python.org/downloads/ (coche *Add python.exe to PATH*).

Rien n'est ecrit hors de ce dossier et de `%APPDATA%\Pystart` (tes donnees) :
pas d'installation systeme, pas d'elevation de droits. Comme rien n'est un
executable compile inconnu, Windows/l'antivirus ne l'affichent pas comme
suspect. Pour mettre a jour : retelecharge le depot (ou `git pull`) et
relance `Pystart.bat`.

### Option installeur Windows (avec mise a jour automatique)

1. Telecharge le fichier `Pystart-Setup-X.Y.Z.exe` depuis la page
   [Releases](https://github.com/kikilikiki/Pystart/releases).
2. Double-clique dessus et suis l'installeur.
3. Lance **Pystart** depuis le menu Demarrer.

Les mises a jour suivantes se font **depuis l'application** (menu _Aide > Mises
a jour_), sans rien retelecharger a la main. L'installeur n'etant pas signe
numeriquement, Windows SmartScreen peut afficher un avertissement
("Editeur inconnu") : clique *Informations complementaires > Executer quand
meme*. Si tu preferes eviter ca, utilise l'option `Pystart.bat` ci-dessus.

### Depuis les sources (developpeurs)

```bash
git clone https://github.com/kikilikiki/Pystart.git
cd Pystart
python -m venv .venv
# Windows :
.venv\Scripts\activate
# Linux / macOS :
source .venv/bin/activate
pip install -r requirements.txt
python -m app
```

## Lancement

```bash
python -m app
```

## Utilisation

1. Choisis un cours dans la colonne de gauche (commence par **01 — Hello World**).
2. Lis la lecon dans le panneau central.
3. Ecris ton code dans l'editeur a droite, clique sur **▶ Executer** (F5).
4. Pour un exercice : clique sur **Verifier**. Utilise les **Indices** si besoin,
   la **solution** seulement en dernier recours.

### Cours

Les cours vivent dans `content/courses/`. Chaque cours est un dossier :

```
content/courses/01_hello_world/
├── course.json        # titre, description, niveau, objectifs
├── lessons/           # *.md, dans l'ordre alphabetique
└── exercises/         # un exercice par fichier .json
```

Ajouter un cours = ajouter un dossier. Aucun code a modifier.
Voir [Docs/courses.md](Docs/courses.md).

### Exercices

Six types : `write`, `modify`, `complete`, `fix`, `predict`, `project`.
La verification s'appuie sur des `checks` (`stdout_equals`, `stdout_contains`,
`no_error`, `source_contains`...). Voir [Docs/exercises.md](Docs/exercises.md).

### Mode professeur

Menu **Professeur** : creer un cours, importer / exporter un cours `.pystart`.
Un cours exporte est une archive ZIP portable a partager avec les eleves.
Voir [Docs/teacher-mode.md](Docs/teacher-mode.md).

## Architecture

```
app/
├── main.py          # point d'entree
├── core/            # chemins, config, version (sans Qt)
├── courses/         # chargement des cours
├── exercises/       # modeles, verification, explications d'erreurs
├── execution/       # execution du code (processus separe)
├── editor/          # editeur + coloration
├── terminal/        # console integree
├── progress/        # base SQLite + migrations
├── teacher/         # creation / export / import de cours
├── libraries/       # environnement virtuel + pip
├── updates/         # detection MAJ + updater separe
└── ui/              # fenetres Qt
content/courses/     # contenu pedagogique
tests/               # pytest
Docs/                # documentation
scripts/             # build, installeur, bump de version
```

Details : [Docs/architecture.md](Docs/architecture.md).

## Developpement

Voir [Docs/development.md](Docs/development.md).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Sous Linux (CI), l'interface tourne en mode « offscreen » :

```bash
QT_QPA_PLATFORM=offscreen pytest
```

## Mises a jour

Les mises a jour proviennent **exclusivement** des
[GitHub Releases officielles](https://github.com/kikilikiki/Pystart/releases).
Pystart compare la version locale a la derniere version publiee, telecharge
l'installeur, verifie sa taille et son empreinte SHA-256, puis lance
`PystartUpdater` qui remplace la version en place et relance l'application.
Details et securite : [Docs/updates.md](Docs/updates.md).

## Contribution

Voir [Docs/contributing.md](Docs/contributing.md).
Messages de commit : `feat:`, `fix:`, `docs:`, `test:`, `release: vX.Y.Z`.

## Licence

MIT — voir [LICENSE](LICENSE).

## Contact

Pour contacter le createur de Pystart :

- Discord : **feelsmanvt**
- Serveur Discord : https://discord.gg/haPVTW3Zqs
- Email : pystartcontact@gmail.com

Projet GitHub : https://github.com/kikilikiki/Pystart

---

## Pour les developpeurs

1. **Cloner** : `git clone https://github.com/kikilikiki/Pystart.git`
2. **Environnement virtuel** :
   `python -m venv .venv` puis activer (`.venv\Scripts\activate` sous Windows).
3. **Dependances** : `pip install -r requirements-dev.txt`
4. **Lancer Pystart** : `python -m app`
5. **Lancer les tests** : `pytest` (ou `QT_QPA_PLATFORM=offscreen pytest`)
6. **Creer un cours** : copier un dossier de `content/courses/`, adapter
   `course.json`, `lessons/` et `exercises/`. Voir [Docs/courses.md](Docs/courses.md).
7. **Creer un exercice** : ajouter un `.json` dans `exercises/` avec `type`,
   `instructions`, `hints`, `solution`, `checks`. Voir [Docs/exercises.md](Docs/exercises.md).
8. **Creer une version** : `python scripts/bump_version.py 0.0.2`
   (met a jour `app/__init__.py` + `CHANGELOG.md`), puis lancer les tests.
9. **Creer une release** : commit, `git tag v0.0.2`, `git push --tags`.
   Le workflow `.github/workflows/release.yml` construit l'exe, l'installeur
   et publie la GitHub Release. Voir [Docs/updates.md](Docs/updates.md).
