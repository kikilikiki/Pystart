# Packages et dependances

La bibliotheque standard ne fait pas tout. **PyPI** (pypi.org) heberge des
centaines de milliers de paquets. On les installe avec **pip**.

## Depuis Pystart

Ouvre **Parametres > Bibliotheques**, tape le nom du paquet (par exemple
`rich` ou `pygame`), clique sur **Installer**. Pystart installe le paquet dans
un **environnement virtuel dedie**, separe de l'application : tes installations
ne peuvent pas casser Pystart.

## En ligne de commande (pour info)

```
python -m pip install rich
```

On ecrit `python -m pip` plutot que `pip` seul pour etre sur d'installer dans
le bon Python.

## Environnement virtuel

Un environnement virtuel est un dossier contenant un Python isole et ses
paquets. Chaque projet a le sien : les versions ne rentrent pas en conflit.

## Exercice

Cet exercice ne verifie que ton **raisonnement** (pas d'execution) : reflechis
a la bonne commande.
