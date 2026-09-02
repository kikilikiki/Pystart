# Les dictionnaires

Un **dictionnaire** associe une **cle** a une **valeur**, entre accolades :

```python
personne = {"nom": "Alice", "age": 20}
print(personne["nom"])    # Alice
personne["age"] = 21      # on modifie
personne["ville"] = "Nice" # on ajoute une nouvelle cle
```

Demander une cle qui n'existe pas provoque une `KeyError`. Pour eviter ca :

```python
print(personne.get("email", "inconnu"))   # inconnu
```

## Parcourir un dictionnaire

```python
for cle, valeur in personne.items():
    print(cle, "->", valeur)
```
