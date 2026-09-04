# Systeme de mise a jour

## Vue d'ensemble

Les mises a jour proviennent **exclusivement** des GitHub Releases officielles :
https://github.com/kikilikiki/Pystart/releases

Pystart **ne fait jamais `git pull`**. L'utilisateur final n'a pas besoin de
Git, Python ni ligne de commande.

> Ceci decrit le systeme de mise a jour de l'**installeur** (`Pystart-Setup-
> X.Y.Z.exe`). En mode lanceur portable (`Pystart.bat`, voir
> `Docs/installation.md`), il n'y a pas de mise a jour en un clic : on
> retelecharge le depot (ou `git pull`) et on relance le script. C'est le
> compromis choisi pour eviter tout executable compile non signe (donc toute
> alerte SmartScreen/antivirus) et toute demande de droits administrateur.

```
Pystart demarre
   |
   v
check()  --->  GET https://api.github.com/repos/kikilikiki/Pystart/releases/latest
   |
   |  compare la version locale (app/__init__.py) a `tag_name`
   |  (comparaison SEMANTIQUE : 0.0.10 > 0.0.9)
   v
Nouvelle version ?  -- non -->  "Vous utilisez la derniere version."
   | oui
   v
[ Mettre a jour ]
   |
   v
download()  --->  telecharge Pystart-Setup-X.Y.Z.exe (asset de la release)
   |
   v
verify()  --->  taille attendue + SHA-256 (si publie dans les notes)
   |
   v
lance PystartUpdater(.exe)  --wait-pid <pid> --installer <exe> --relaunch <exe>
   |
   v
Pystart se ferme
   |
   v
Updater : attend la fermeture -> lance l'installeur /SILENT -> relance Pystart
```

## Comparaison des versions

`app/core/version.py` s'appuie sur `packaging.version.Version`. **Jamais** de
comparaison de chaines : `"0.0.9" < "0.0.10"` est faux lettre par lettre.

## Securite

| Mesure | Details |
|---|---|
| HTTPS obligatoire | seules `github.com`, `api.github.com`, `objects.githubusercontent.com` sont acceptees |
| Pas d'URL arbitraire | l'URL de telechargement vient de l'API GitHub, jamais d'une saisie |
| Verification de taille | on compare a `asset.size` renvoye par GitHub |
| SHA-256 | si les notes de release contiennent `SHA-256: <64 hex>` ou une ligne `Pystart-Setup-X.Y.Z.exe <64 hex>`, l'empreinte est verifiee ; sinon on s'appuie sur HTTPS + taille |
| Pas de suppression prematuree | l'installeur ecrit par-dessus ; l'ancienne version n'est retiree qu'apres installation reussie |
| Rollback | si l'installeur echoue (code != 0), l'updater n'y touche pas et l'ancienne version reste utilisable |

## Updater separe

Sous Windows, un programme ne peut pas se remplacer lui-meme pendant qu'il
tourne. `app/updates/updater_cli.py` (compile en `PystartUpdater.exe`) :

1. attend la fin du processus Pystart (`--wait-pid`) ;
2. lance l'installeur : `Pystart-Setup-X.Y.Z.exe /SILENT /NORESTART` ;
3. relance Pystart (`--relaunch`) ;
4. en cas d'echec, **ne modifie rien**.

En mode developpement (non compile), Pystart appelle
`python -m app.updates.updater_cli` a la place.

## Mises a jour obligatoires

Si les notes de la release contiennent le marqueur `[mandatory]` (ou
`[obligatoire]`), l'application signale une **mise a jour obligatoire**.
L'utilisateur est fortement incite a l'installer. Si le telechargement echoue,
l'application **reste utilisable** (pas de blocage sans issue).

## Conservation des donnees

L'installeur n'ecrit que dans le dossier programme. Les donnees utilisateur
(`%APPDATA%\Pystart` : `pystart.db`, `config.json`, cours perso, projets) ne
sont **jamais** touchees. Le schema SQLite evolue par **migrations**
(`app/progress/store.py`, `PRAGMA user_version`) : `Database v1 -> migration ->
Database v2`, sans perte.

---

## Build : produire l'exe et l'installeur

### 1. Executable (PyInstaller)

```bash
pip install -r requirements-dev.txt
python scripts/build.py
```

Produit `dist/Pystart/Pystart.exe` et `dist/Pystart/PystartUpdater.exe`, avec
le dossier `content/` embarque.

### 2. Installeur (Inno Setup, Windows)

Installe [Inno Setup](https://jrsoftware.org/isdl.php), puis :

```bash
iscc scripts/Pystart.iss
```

Produit `dist/Pystart-Setup-X.Y.Z.exe` (le numero vient de `app/__init__.py`).

### 3. Archive portable (`Pystart.bat`)

```bash
python scripts/build_portable_zip.py
```

Produit `dist/Pystart-Portable-X.Y.Z.zip` : uniquement les sources +
`Pystart.bat` (pas de compilation). C'est l'asset attache a la Release pour
l'installation sans admin / sans alerte antivirus (voir Docs/installation.md).

### 4. Release

Voir la section suivante — c'est automatise par GitHub Actions au push d'un
tag `vX.Y.Z`.

---

## Procedure de release (ex. 0.0.1 -> 0.0.2)

```bash
python scripts/bump_version.py 0.0.2      # met a jour app/__init__.py + CHANGELOG
# completer la section [0.0.2] du CHANGELOG a la main
pytest                                    # 1. tests
git add -A && git commit -m "release: v0.0.2"
git tag v0.0.2
git push origin main --tags               # 2. declenche release.yml
```

Le workflow `.github/workflows/release.yml` (runner Windows) :

3. installe les dependances ;
4. relance les tests ;
5. `python scripts/build.py` (PyInstaller) ;
6. `iscc scripts/Pystart.iss` (installeur) ;
7. calcule le SHA-256 de l'exe ;
8. cree la **GitHub Release** `v0.0.2` et y **attache** `Pystart-Setup-0.0.2.exe`
   (+ le SHA-256 dans les notes).

### Etapes qui peuvent demander une action manuelle

- **Authentification GitHub** : le workflow utilise `GITHUB_TOKEN` fourni
  automatiquement par Actions. Si tu publies a la main (`gh release create`),
  il te faut `gh auth login`.
- **Signature de l'exe** : non configuree (pas de certificat). SmartScreen
  affichera un avertissement « editeur inconnu » tant qu'aucun certificat de
  signature de code n'est ajoute.

Ne considere jamais une release comme faite tant que le fichier
`Pystart-Setup-X.Y.Z.exe` n'est pas **telechargeable** depuis la page Releases
et que _Aide > Mises a jour_ ne detecte pas la nouvelle version.

## Tester une mise a jour 0.0.1 -> 0.0.2

1. Installe 0.0.1 avec l'installeur.
2. Publie 0.0.2 (ou une release de test).
3. Dans Pystart 0.0.1 : _Aide > Mises a jour > Verifier_.
4. Verifie : detection, telechargement, verification, fermeture, installation,
   redemarrage en 0.0.2, **progression conservee**.
