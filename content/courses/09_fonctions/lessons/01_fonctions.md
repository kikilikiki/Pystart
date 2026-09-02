# Les fonctions

Une **fonction** regroupe des instructions sous un nom, pour les reutiliser.

```python
def say_hello(name):
    print(f"Bonjour {name}")

say_hello("Alice")
say_hello("Sam")
```

- `def` demarre la definition.
- `name` est un **parametre** (une variable qui recevra la valeur donnee).
- Le corps est indente.

## Renvoyer une valeur avec `return`

`print` **affiche** ; `return` **renvoie** une valeur utilisable ensuite.

```python
def carre(x):
    return x * x

resultat = carre(5)
print(resultat)   # 25
```

Des que Python rencontre `return`, il sort de la fonction.

## Valeurs par defaut

```python
def salut(name, message="Bonjour"):
    print(f"{message} {name}")

salut("Alice")             # Bonjour Alice
salut("Sam", "Coucou")     # Coucou Sam
```
