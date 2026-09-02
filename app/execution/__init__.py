"""Execution du code ecrit par l'utilisateur.

REGLE DE SECURITE FONDAMENTALE
------------------------------
Le code de l'utilisateur n'est JAMAIS execute dans le processus de Pystart.
Il tourne toujours dans un processus Python separe que l'on peut arreter,
limiter dans le temps et dont on capture la sortie.

LIMITE DE SECURITE (a lire absolument)
-------------------------------------
Un processus separe n'est PAS une sandbox. Le code lance a les memes droits
que l'utilisateur : il peut lire/ecrire des fichiers, acceder au reseau, etc.
Pystart reduit les risques (isolation par `-I`, timeout, dossier de travail
dedie) mais NE garantit PAS une execution sans danger. Voir Docs/execution.md.
"""
