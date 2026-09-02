# Les types de donnees

Toute valeur en Python a un **type**. Les quatre types de base :

| Type    | Exemple        | Signification              |
|---------|----------------|----------------------------|
| `str`   | `"bonjour"`    | une chaine de caracteres   |
| `int`   | `42`           | un nombre entier           |
| `float` | `3.14`         | un nombre a virgule        |
| `bool`  | `True` / `False` | vrai ou faux             |

La fonction `type()` donne le type d'une valeur :

```python
print(type("bonjour"))   # <class 'str'>
print(type(42))          # <class 'int'>
print(type(3.14))        # <class 'float'>
print(type(True))        # <class 'bool'>
```

## Convertir d'un type a l'autre

```python
age_texte = "20"
age = int(age_texte)     # "20" -> 20
print(age + 1)           # 21
```

- `int("20")` -> `20`
- `float("3.5")` -> `3.5`
- `str(20)` -> `"20"`

Attention : `int("bonjour")` provoque une erreur `ValueError`.

## Melanger des types

On ne peut pas additionner un texte et un nombre :

```python
print("age : " + 20)     # TypeError !
print("age : " + str(20)) # OK -> age : 20
```
