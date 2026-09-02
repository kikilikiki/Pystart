# Les exceptions

Quand une erreur survient, Python **leve une exception**. Sans traitement, le
programme s'arrete et affiche un *traceback*.

```python
try:
    age = int(input("Ton age ? "))
    print(f"L'an prochain : {age + 1}")
except ValueError:
    print("Ce n'est pas un nombre entier.")
```

## Attraper l'exception PRECISE

Ecris toujours le type attendu (`ValueError`, `ZeroDivisionError`, `KeyError`...).

**Evite** `except:` tout seul (ou `except Exception:`) : il attrape TOUT, y
compris les erreurs que tu n'avais pas prevues, et masque les vrais bugs.

```python
# A eviter
try:
    faire_quelque_chose()
except:
    pass          # on ne sait meme pas ce qui a rate !
```

## else et finally

```python
try:
    valeur = donnees["cle"]
except KeyError:
    print("cle absente")
else:
    print("tout va bien :", valeur)   # si aucune exception
finally:
    print("on nettoie")               # dans tous les cas
```
