# Creer un cours

Un cours est un **dossier** dans `content/courses/` (cours livres) ou dans
`%APPDATA%\Pystart\courses\` (cours perso / professeur).

## Structure

```
mon_cours/
├── course.json         # obligatoire : metadonnees
├── lessons/            # optionnel : lecons en Markdown
│   ├── 01_intro.md
│   └── 02_pour_aller_plus_loin.md
└── exercises/          # optionnel : un exercice par fichier JSON
    ├── 01_premier.json
    └── 02_deuxieme.json
```

L'identifiant du cours est le **nom du dossier** (ex. `01_hello_world`).
Les lecons et exercices sont tries par **ordre alphabetique du nom de fichier** :
prefixe-les par `01_`, `02_`...

## `course.json`

```json
{
  "title": "17 — Mon super cours",
  "description": "Ce que le cours apprend, en une ou deux phrases.",
  "level": "debutant",
  "order": 17,
  "objectives": ["Objectif 1", "Objectif 2"],
  "prerequisites": ["16 — Mini-projets"]
}
```

| Champ | Role |
|---|---|
| `title` | affiche dans l'arbre et l'entete |
| `description` | resume du cours |
| `level` | `debutant`, `intermediaire` ou `avance` (indicatif) |
| `order` | position dans la liste (nombre) |
| `objectives` | liste de ce qu'on saura faire |
| `prerequisites` | liste de cours conseilles avant |

## Lecons (`lessons/*.md`)

Du Markdown standard. Le premier titre `# ...` devient le titre de la lecon.
Les blocs de code ` ```python ` sont affiches en police a chasse fixe.

Conseil pedagogique : suis le parcours
**explication -> exemple -> (renvoi vers l'exercice)**.

## Exercices

Un fichier JSON par exercice dans `exercises/`. Voir
[exercises.md](exercises.md) pour le format complet.

## Cours livre vs cours utilisateur

- Si un cours utilisateur a le **meme nom de dossier** qu'un cours livre, il le
  **remplace**.
- Les cours utilisateur portent la mention `source = "user"` (utile pour
  l'export).

## Verifier son cours

Relance Pystart : le cours apparait dans l'arbre. Teste chaque exercice avec sa
propre solution. En developpement :

```bash
pytest tests/test_course_loader.py tests/test_validator.py
```

Le test `test_reference_solution_passes` execute la solution de **chaque**
exercice et verifie qu'elle passe tous les `checks`.
