# Les boucles

## La boucle `for` et `range()`

`for` repete un bloc pour chaque valeur d'une suite. `range(n)` produit les
nombres de `0` a `n - 1` :

```python
for i in range(5):
    print(i)
# affiche 0 1 2 3 4 (un par ligne)
```

- `range(1, 6)` -> 1, 2, 3, 4, 5
- `range(0, 10, 2)` -> 0, 2, 4, 6, 8 (pas de 2)

## La boucle `while`

`while` repete **tant que** la condition est vraie :

```python
compte = 3
while compte > 0:
    print(compte)
    compte = compte - 1
print("Partez !")
```

Il faut que quelque chose fasse **evoluer** la condition, sinon la boucle ne
s'arrete jamais (boucle infinie). Pystart coupe les programmes trop longs
grace a un delai maximum.
