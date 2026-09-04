# Installation

Pystart propose deux facons de l'installer sous Windows. Le lanceur `.bat` est
recommande si tu veux eviter tout avertissement Windows/antivirus ou toute
demande de droits administrateur (voir `Docs/execution.md` et
`Docs/updates.md` pour le detail des compromis).

## Option A — `Pystart.bat` (sans admin, sans alerte)

Ce n'est pas un executable compile : c'est un script qui utilise ton propre
Python. Rien n'est installe au niveau systeme, donc rien a signer et rien qui
ressemble a un programme inconnu pour Windows Defender.

1. Telecharge le depot : bouton **Code > Download ZIP** sur GitHub (ou
   `git clone https://github.com/kikilikiki/Pystart.git`), puis decompresse.
2. Double-clique sur `Pystart.bat`.
   - S'il ne trouve pas de Python 3.10+, il ouvre la page de telechargement
     officielle (https://www.python.org/downloads/) et s'arrete : installe
     Python (coche *Add python.exe to PATH*), relance le script.
   - Au premier lancement, il cree un environnement virtuel local
     (`.pystart-venv`, a cote du script) et y installe les dependances de
     Pystart (`requirements.txt`). Les lancements suivants demarrent
     directement.
3. Pystart s'ouvre.

**Mettre a jour :** retelecharge le depot (ou `git pull`) et relance le
script — pas de systeme de mise a jour en un clic dans ce mode (voir
`Docs/updates.md`).

**Desinstaller :** supprime simplement le dossier telecharge. Tes donnees
(profil, progression, cours perso) restent dans `%APPDATA%\Pystart` — a
supprimer a part si tu veux tout effacer.

## Option B — installeur Windows (`Pystart-Setup-X.Y.Z.exe`)

Avantage : mise a jour en un clic depuis l'application. Inconvenient :
l'installeur n'est pas signe numeriquement, donc Windows SmartScreen peut
afficher un avertissement.

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
| L'installeur Windows est bloque | verifie l'antivirus, l'exe n'est pas signe pour l'instant ; sinon utilise `Pystart.bat` (Option A) |
| `Pystart.bat` : "Python n'a pas ete trouve" | installe Python depuis python.org en cochant *Add python.exe to PATH*, relance le script |
| `Pystart.bat` tres lent au 1er lancement | normal : installation des dependances (~1-2 min). Les lancements suivants sont rapides |
| Recommencer `Pystart.bat` de zero | supprime le dossier `.pystart-venv` puis relance le script |
