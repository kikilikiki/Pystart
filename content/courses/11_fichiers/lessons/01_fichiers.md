# Les fichiers

## Ecrire

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("Premiere ligne\n")
    f.write("Deuxieme ligne\n")
```

- `"w"` : mode ecriture (ecrase le fichier s'il existe).
- `"a"` : mode ajout (ecrit a la fin).
- Le bloc `with` **ferme** le fichier automatiquement a la fin.

## Lire

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    contenu = f.read()
print(contenu)
```

Pour parcourir ligne par ligne :

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    for ligne in f:
        print(ligne.strip())
```

Dans Pystart, les fichiers crees par ton programme apparaissent dans le
dossier de travail (workspace).
