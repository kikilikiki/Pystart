# Guide de developpement

## Mettre en place l'environnement

```bash
git clone https://github.com/kikilikiki/Pystart.git
cd Pystart
python -m venv .venv
source .venv/bin/activate        # ou .venv\Scripts\activate sous Windows
pip install -r requirements-dev.txt
```

## Lancer l'application

```bash
python -m app
```

Le mode developpement ecrit ses donnees dans le dossier systeme habituel.
Pour isoler (recommande pendant le dev) :

```bash
# Windows PowerShell
$env:PYSTART_DATA_DIR = "$PWD/.pystart-dev"; python -m app
# Bash
PYSTART_DATA_DIR="$PWD/.pystart-dev" python -m app
```

## Tests

```bash
pytest                              # tout
pytest tests/test_validator.py -q   # un fichier
QT_QPA_PLATFORM=offscreen pytest    # sans serveur graphique (CI Linux)
```

Les tests forcent `PYSTART_DATA_DIR` vers un dossier temporaire
(`tests/conftest.py`) : ils n'ecrasent jamais tes vraies donnees.

## Lint

```bash
ruff check .
ruff check . --fix
```

## Organisation du code

- Un fichier = une responsabilite. Evite les fichiers de plusieurs milliers de
  lignes.
- `app/core` ne doit **jamais** importer PySide6.
- Toute operation longue dans l'UI passe par un `QThread` + signaux (voir
  `ValidationWorker`, `_CheckWorker`, `_InstallWorker`).
- Type hints partout ; docstrings sur les classes et fonctions non triviales ;
  commentaires qui expliquent le **pourquoi** et les **concepts Python**.

## Ajouter une fonctionnalite

1. Ecris/adapte le code metier dans le bon paquet.
2. Ajoute des tests.
3. `pytest` + `ruff check .`.
4. Lance l'app, verifie a la main.
5. Mets a jour la doc concernee et `CHANGELOG.md` (section « Non publie »).

## Construire l'executable et l'installeur

Voir [updates.md](updates.md) section « Build ». En resume :

```bash
python scripts/build.py             # -> dist/Pystart/ (PyInstaller)
# puis, sous Windows avec Inno Setup installe :
iscc scripts/Pystart.iss            # -> dist/Pystart-Setup-X.Y.Z.exe
```

## Changer de version

```bash
python scripts/bump_version.py 0.0.2
```

Ce script modifie **uniquement** `app/__init__.py` et prepare `CHANGELOG.md`.
Voir [updates.md](updates.md) pour la procedure de release complete.
