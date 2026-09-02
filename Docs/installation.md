# Installation

## Utilisateur final (Windows)

1. Va sur https://github.com/kikilikiki/Pystart/releases
2. Telecharge `Pystart-Setup-X.Y.Z.exe` (la version la plus recente).
3. Double-clique. Windows peut afficher un avertissement SmartScreen pour un
   editeur inconnu : clique sur « Informations complementaires » puis
   « Executer quand meme ».
4. Suis l'assistant d'installation.
5. Lance **Pystart** depuis le menu Demarrer ou le raccourci du bureau.

### Desinstallation

Panneau de configuration > Programmes > Pystart > Desinstaller.
**Tes cours perso et ta progression ne sont pas supprimes** : ils restent dans
`%APPDATA%\Pystart`. Supprime ce dossier manuellement si tu veux tout effacer.

## Depuis les sources (tout systeme)

Prerequis : **Python 3.10+**.

```bash
git clone https://github.com/kikilikiki/Pystart.git
cd Pystart

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
python -m app
```

Pour developper (tests, lint, build) :

```bash
pip install -r requirements-dev.txt
```

## Depannage

| Probleme | Solution |
|---|---|
| `ModuleNotFoundError: PySide6` | `pip install -r requirements.txt` dans le bon venv |
| Rien ne s'affiche sous Linux sans ecran | `QT_QPA_PLATFORM=offscreen` (pour les tests uniquement) |
| `python` lance Python 2 | utilise `python3` / `py -3` |
| L'installeur Windows est bloque | verifie l'antivirus, l'exe n'est pas signe pour l'instant |
