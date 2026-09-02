# Architecture de Pystart

## Principes

1. **Separer les responsabilites.** Interface, logique metier, contenu,
   execution, progression, professeur et mises a jour sont des paquets
   distincts.
2. **Le contenu n'est pas dans le code.** Les cours sont des fichiers
   (`content/courses/`). Ajouter un cours ne demande aucune modification du
   moteur.
3. **Le code utilisateur est isole.** Il tourne toujours dans un processus
   Python separe.
4. **Le code source est pedagogique.** Noms explicites, fonctions courtes,
   docstrings, commentaires qui expliquent les concepts (subprocess, SQLite,
   signaux Qt, JSON, venv...).

## Choix de la technologie d'interface : PySide6 (Qt)

**PySide6** est le binding Python officiel de Qt (sous licence LGPL).

Pourquoi PySide6 plutot qu'une autre solution ?

| Critere | PySide6 | Tkinter | Web (Electron/PyWebView) |
|---|---|---|---|
| Widgets riches (arbre, splitters, editeur) | ✅ natif | ⚠️ limite | ✅ mais lourd |
| Editeur de code (`QPlainTextEdit` + `QSyntaxHighlighter`) | ✅ | ❌ a faire soi-meme | ✅ |
| Processus externes integres a la boucle d'evenements (`QProcess`) | ✅ | ❌ | ⚠️ |
| Taille de l'executable | moyenne | petite | grande |
| Rendu Markdown integre (`QTextBrowser.setMarkdown`) | ✅ | ❌ | ✅ |
| Multiplateforme, apparence native | ✅ | ⚠️ | ✅ |

PySide6 offre le meilleur compromis pour une application desktop avec un
editeur, un terminal et des panneaux redimensionnables, tout en gardant un
code lisible.

## Couches

```
+-------------------------------------------------------------+
|                        app/ui  (Qt)                         |
|  main_window, exercise_panel, dialogs, theme                |
+-------------------------------------------------------------+
        |            |             |            |
        v            v             v            v
   app/courses   app/exercises  app/progress  app/updates
   (loader)      (validator)    (SQLite)      (GitHub)
        |            |
        +------------+
              v
        app/execution  --->  processus Python separe
              ^
        app/core (paths, config, version)  -- sans Qt, testable seul
```

- `app/core` ne connait pas Qt : on peut le tester sans interface.
- `app/ui` ne contient pas de logique metier ; il appelle les autres paquets.
- La communication interface <-> travail long passe par des **signaux Qt** et
  des `QThread` (verification d'exercice, verification de MAJ, installation pip).

## Flux : verifier un exercice

```
Editeur (code)                Panneau exercice           Processus Python
     |                              |                          |
     |  clic "Verifier"             |                          |
     |----------------------------->| ValidationWorker (thread)|
     |                              |  run_script(code) ------->| execute -I main.py
     |                              |<---------- stdout/stderr -|
     |                              | applique les checks       |
     |<-- signal check_completed ---|                          |
  enregistre l'essai (SQLite), rafraichit l'arbre et la barre d'etat
```

## Donnees

- **Livrees avec l'app** (lecture seule) : `content/` (cours par defaut).
- **De l'utilisateur** (jamais supprimees a la MAJ) : dossier de donnees
  systeme (`%APPDATA%/Pystart` sous Windows) contenant `pystart.db`,
  `config.json`, `courses/` (cours perso), `projects/`, `workspace/`,
  `user-venv/`, `updates/`, `logs/`.
- `PYSTART_DATA_DIR` permet de rediriger ce dossier (tests, mode dev).

## Version : source unique

`app/__init__.py` -> `__version__`. Tout le reste (page "A propos", updater,
`pyproject.toml` via `dynamic`, workflow de release) lit cette valeur.
`scripts/bump_version.py` est le seul a la modifier.
