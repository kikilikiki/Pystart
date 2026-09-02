# Les classes

Une **classe** decrit un type d'objet. Chaque objet cree (une **instance**) a
ses propres donnees.

```python
class Chien:
    def __init__(self, nom):
        self.nom = nom          # attribut propre a l'instance

    def aboyer(self):
        print(f"{self.nom} : Wouf !")

rex = Chien("Rex")
rex.aboyer()                    # Rex : Wouf !
```

- `__init__` est le **constructeur** : appele automatiquement a la creation.
- `self` represente l'objet courant ; il est toujours le premier parametre
  d'une methode.

## Plusieurs instances independantes

```python
a = Chien("Rex")
b = Chien("Bella")
print(a.nom, b.nom)   # Rex Bella
```
