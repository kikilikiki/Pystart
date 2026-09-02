# Les conditions

Une condition execute du code **seulement si** quelque chose est vrai.

```python
age = 20

if age >= 18:
    print("Majeur")
else:
    print("Mineur")
```

- La ligne `if` se termine par `:`.
- Le bloc a executer est **indente de 4 espaces**.
- `else` (« sinon ») est optionnel.

## Les operateurs de comparaison

| Operateur | Sens              |
|-----------|-------------------|
| `==`      | egal a            |
| `!=`      | different de      |
| `<` `>`   | inferieur / superieur |
| `<=` `>=` | inferieur/superieur ou egal |

Attention : `=` sert a **affecter** une variable, `==` sert a **comparer**.

## Plusieurs cas avec elif

```python
note = 12

if note >= 16:
    print("Tres bien")
elif note >= 12:
    print("Bien")
elif note >= 10:
    print("Passable")
else:
    print("Insuffisant")
```

Python teste les cas **dans l'ordre** et s'arrete au premier qui est vrai.
