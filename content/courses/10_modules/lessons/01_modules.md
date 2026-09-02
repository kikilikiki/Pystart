# Les modules

Un **module** contient des fonctions deja ecrites. La bibliotheque standard de
Python en fournit des centaines.

```python
import math
print(math.sqrt(16))    # 4.0
print(math.pi)          # 3.141592653589793
```

## Importer seulement ce qu'on veut

```python
from random import randint
print(randint(1, 6))    # un entier au hasard entre 1 et 6
```

## Quelques modules utiles

- `math` : racines, puissances, arrondis, constantes.
- `random` : tirages aleatoires.
- `datetime` : dates et heures.
- `statistics` : moyenne, mediane...
