# Execution du code utilisateur

## Regle fondamentale

Le code ecrit par l'utilisateur (ou provenant d'un cours importe) **n'est
jamais** execute dans le processus de Pystart. Il tourne dans un **processus
Python separe**.

```
Pystart (interface)
   |
   |  ecrit le code dans workspace/main.py
   |  lance :  python -I -u main.py
   v
Processus Python utilisateur
   ├── stdout ─┐
   ├── stderr ─┼─> captures, affichees dans le terminal
   └── exit code ┘
```

Deux implementations :

| Contexte | Module | Mecanisme |
|---|---|---|
| Bouton « Executer » (interactif) | `app/execution/process_runner.py` | `QProcess` + signaux, `input()` possible, bouton Stop |
| Verification d'exercice (en thread) | `app/execution/runner.py` | `subprocess.run(..., timeout=...)` |

## Protections en place

- **Processus separe** : un plantage du code n'affecte pas Pystart.
- **Mode isole `-I`** : ignore `PYTHON*`, le `site` utilisateur et le dossier
  courant dans `sys.path`.
- **Timeout** : le processus est tue au-dela du delai (8 s par defaut pour les
  exercices, 20 s pour l'execution manuelle, infini-loop coupee).
- **Bouton Stop** : `kill()` immediat.
- **Sortie bornee** : au-dela de ~200 000 caracteres, la sortie est coupee.
- **Dossier de travail dedie** : `workspace/`, pas le dossier de l'app.

## Ce qui N'EST PAS protege — limites de securite

**Un `subprocess` n'est PAS une sandbox.** Le code execute a **les memes droits
que l'utilisateur** qui a lance Pystart. Il peut :

- lire, modifier ou supprimer les fichiers de l'utilisateur ;
- ouvrir des connexions reseau ;
- lancer d'autres programmes ;
- consommer CPU / RAM / disque (le timeout limite surtout le temps).

Pystart **ne pretend pas** offrir une execution sans danger. Recommandations :

- n'importe **que** des cours provenant de personnes de confiance
  (ton professeur, le depot officiel) ;
- ne colle pas de code inconnu trouve sur Internet pour « voir ce qu'il fait ».

Une vraie isolation (conteneur, machine virtuelle, `seccomp`, WASM...) pourra
etre ajoutee dans une version ulterieure ; c'est hors perimetre de la 0.0.x.

## Rendre les erreurs comprehensibles

`app/exercises/errors.py` analyse le `stderr` et ajoute, **en plus du traceback
reel**, une explication en francais et un indice cible (`NameError`,
`SyntaxError`, `IndentationError`, `TypeError`, `ModuleNotFoundError`...).
Le traceback complet reste toujours accessible.
