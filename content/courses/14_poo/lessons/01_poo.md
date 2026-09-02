# Programmation orientee objet

## Des methodes qui collaborent

```python
class CompteBancaire:
    def __init__(self, solde=0):
        self.solde = solde

    def depot(self, montant):
        self.solde += montant

    def retrait(self, montant):
        if montant > self.solde:
            print("Fonds insuffisants")
            return
        self.solde -= montant
```

## L'heritage

Une classe peut **heriter** d'une autre : elle recupere ses attributs et
methodes, et peut en ajouter ou en redefinir.

```python
class Animal:
    def __init__(self, nom):
        self.nom = nom

    def decrire(self):
        return self.nom

class Chat(Animal):
    def crier(self):
        return f"{self.nom} : Miaou"

felix = Chat("Felix")
print(felix.decrire())   # herite d'Animal -> Felix
print(felix.crier())     # propre a Chat  -> Felix : Miaou
```

`super().__init__(...)` permet d'appeler le constructeur de la classe parente.
