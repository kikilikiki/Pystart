# Les variables

## Une étiquette sur une valeur

Une **variable** garde une valeur en mémoire sous un nom que tu choisis.
On la crée avec le signe `=` (qu'on lit « reçoit ») :

```python
name = "Alice"
age = 20

print(name)
print(age)
```

Résultat :

```
Alice
20
```

- À **gauche** du `=` : le nom de la variable.
- À **droite** : la valeur qu'elle reçoit.

## Réutiliser et modifier

Une variable peut changer de valeur :

```python
score = 0
score = score + 10
print(score)   # 10
```

## Afficher plusieurs choses

`print()` accepte plusieurs valeurs séparées par des virgules. Il insère un
espace entre elles :

```python
name = "Alice"
print("Bonjour", name)      # Bonjour Alice
```

## Les f-strings (chaînes formatées)

Pour insérer une variable **dans** un texte, préfixe la chaîne par `f` et mets
la variable entre accolades :

```python
name = "Alice"
age = 20
print(f"{name} a {age} ans")   # Alice a 20 ans
```

## Bien nommer ses variables

- Des lettres, des chiffres et des `_` (mais pas de chiffre en premier).
- Un nom clair : `age_utilisateur` plutôt que `x`.
- Python distingue les majuscules : `age` et `Age` sont deux variables différentes.
