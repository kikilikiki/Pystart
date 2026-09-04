# Changelog

Toutes les modifications notables de Pystart sont consignees ici.

Le format s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le projet suit le [versionnement semantique](https://semver.org/lang/fr/)
`MAJOR.MINOR.PATCH`.

## [Non publie]

### Added

- `Pystart.bat` : lanceur portable sans installeur. Aucun executable compile
  (donc aucune alerte SmartScreen/antivirus) et aucun droit administrateur :
  le script detecte Python, cree un environnement virtuel local
  (`.pystart-venv`) et installe les dependances au premier lancement.

### Fixed

- Bouton *Aide > Mises a jour* affichait "impossible de contacter GitHub"
  quand le depot n'avait encore aucune release (HTTP 404 sur
  `/releases/latest`, mal interprete comme une erreur reseau).
- Changer d'exercice declenchait une boite de dialogue "remplacer le code ?"
  a chaque fois. Chaque exercice garde maintenant son propre brouillon de
  code (sauvegarde entre deux lancements).
- Theme sombre : les panneaux de lecon/resultat (Markdown) restaient sur
  fond blanc. Migration vers une vraie `QPalette` en plus du QSS.
- CI : les tests echouaient a la collecte (`ModuleNotFoundError: No module
  named 'app'`) car le workflow lancait `pytest` sans `python -m` ; ajout de
  `pythonpath = ["."]` dans la configuration pytest.

## [0.0.1] - 2026-09-02

### Added

- Interface desktop (PySide6) a trois panneaux redimensionnables :
  arbre des cours, panneau lecon/exercice, editeur Python.
- Terminal / console integre affichant stdout, stderr et les tracebacks.
- Editeur Python : coloration syntaxique, numeros de lignes, auto-indentation,
  Tab / Shift+Tab, thèmes clair et sombre.
- Execution du code utilisateur dans un **processus separe** avec timeout,
  bouton Stop et limitation de la sortie.
- Moteur d'exercices : 6 types (ecrire, modifier, completer, corriger,
  predire, projet) et verification automatique (`stdout_equals`,
  `stdout_contains`, `stdout_matches`, `no_error`, `source_contains`...).
- Indices progressifs et solution revelable a la demande (jamais automatique).
- Explications d'erreurs en francais, en plus du traceback reel.
- 16 cours (Hello World -> mini-projets), 27 exercices, tous verifies.
- Progression sauvegardee en SQLite (profils, exercices reussis, cours
  termines, journal d'activite) avec systeme de migrations.
- Mode professeur : creation de cours, export/import `.pystart` (ZIP) avec
  validation stricte (anti path-traversal, extensions autorisees, taille max).
- Installation de bibliotheques externes (pip) dans un environnement virtuel
  dedie a l'utilisateur, isole de Pystart.
- Systeme de mise a jour : detection via GitHub Releases, comparaison
  semantique des versions, telechargement verifie (taille + SHA-256),
  updater separe `PystartUpdater`.
- Page "A propos" avec liens Discord, e-mail et GitHub.
- Documentation (`Docs/`), tests (`pytest`), workflows GitHub Actions,
  specification PyInstaller et script d'installeur Inno Setup.

[Non publie]: https://github.com/kikilikiki/Pystart/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/kikilikiki/Pystart/releases/tag/v0.0.1
