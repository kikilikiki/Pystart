"""Installation de bibliotheques Python externes (pygame, etc.).

Principe : les dependances installees par l'utilisateur vont dans un
environnement virtuel DEDIE, separe de l'environnement interne de Pystart.
Ainsi, installer `pygame` pour un projet ne casse jamais l'application.

On utilise toujours `python -m pip` (jamais `pip` tout court) pour etre sur
de viser le bon interpreteur.
"""
