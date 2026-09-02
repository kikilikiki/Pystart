# Les entrees utilisateur

`input()` **met le programme en pause**, attend que la personne tape quelque
chose et appuie sur Entree, puis renvoie ce texte.

```python
name = input("Quel est ton nom ? ")
print(f"Bonjour {name}")
```

Dans Pystart, quand un programme appelle `input()`, tu reponds dans le champ
de saisie **sous le terminal**, puis tu cliques sur **Envoyer**.

## input() renvoie TOUJOURS du texte

Meme si la personne tape `25`, `input()` renvoie la chaine `"25"`.
Pour calculer avec, il faut convertir :

```python
age_texte = input("Ton age ? ")
age = int(age_texte)
print(f"L'an prochain tu auras {age + 1} ans")
```
