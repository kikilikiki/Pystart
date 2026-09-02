# Les listes

Une **liste** contient plusieurs valeurs, entre crochets, separees par des virgules :

```python
fruits = ["pomme", "banane", "kiwi"]
print(fruits[0])    # pomme  (le premier element a l'indice 0)
print(fruits[-1])   # kiwi   (indice negatif = depuis la fin)
print(len(fruits))  # 3      (nombre d'elements)
```

## Modifier une liste

```python
fruits.append("orange")   # ajoute a la fin
fruits[1] = "fraise"      # remplace l'element d'indice 1
```

## Parcourir une liste

```python
for fruit in fruits:
    print(fruit)
```

Erreur classique : `IndexError` quand on demande un indice qui n'existe pas
(par exemple `fruits[10]` alors que la liste a 4 elements).
