# Creer un exercice

Un exercice = un fichier `.json` dans le dossier `exercises/` d'un cours.

## Exemple minimal

```json
{
  "id": "01_hello_world.afficher_bonjour",
  "type": "write",
  "title": "Afficher Bonjour",
  "instructions": "Ecris un programme qui affiche `Bonjour !`.",
  "starter_code": "",
  "hints": ["Utilise print().", "Le texte va entre guillemets."],
  "solution": "print(\"Bonjour !\")",
  "checks": [
    { "kind": "no_error" },
    { "kind": "stdout_equals", "value": "Bonjour !" }
  ]
}
```

## Champs

| Champ | Obligatoire | Role |
|---|---|---|
| `id` | oui | identifiant unique (`<cours>.<slug>`) |
| `type` | oui | `write`, `modify`, `complete`, `fix`, `predict`, `project` |
| `title` | oui | titre court |
| `instructions` | oui | consigne (Markdown accepte) |
| `starter_code` | non | code pre-rempli dans l'editeur |
| `hints` | non | liste d'indices reveles un par un |
| `solution` | non | code complet, revele a la demande |
| `checks` | non | verifications automatiques (voir plus bas) |
| `stdin` | non | texte fourni sur l'entree standard (`input()`) |
| `timeout_seconds` | non | delai max d'execution (defaut 8) |
| `choices` | pour `predict` | options proposees |
| `order` | non | position dans la liste |

## Les 6 types

| Type | Usage | Editeur |
|---|---|---|
| `write` | ecrire un programme a partir de rien | vide |
| `modify` | modifier un programme existant | `starter_code` |
| `complete` | remplir des trous (`____`) | `starter_code` |
| `fix` | corriger un bug | `starter_code` (bugue) |
| `predict` | quiz : « que va afficher ce programme ? » | pas d'editeur, des `choices` |
| `project` | projet plus libre, verifie par la sortie | `starter_code` (squelette) |

## Les verifications (`checks`)

Chaque check a un `kind`, une `value` et un `message` optionnel affiche en cas
d'echec.

| `kind` | Verifie que... |
|---|---|
| `no_error` | le programme se termine sans exception (code 0) |
| `stdout_equals` | la sortie == `value` (espaces de fin ignores) |
| `stdout_contains` | la sortie contient `value` |
| `stdout_not_contains` | la sortie ne contient pas `value` |
| `stdout_matches` | la sortie correspond a l'expression reguliere `value` |
| `source_contains` | le code source contient `value` (ex. `"for "`) |
| `source_not_contains` | le code source ne contient pas `value` (ex. `"____"`) |
| `choice_equals` | (`predict`) la reponse choisie == `value` |

### Conseils

- Commence toujours par `no_error` : le message d'erreur guide l'eleve.
- Pour les exercices avec `input()`, mets un `stdin` et **evite**
  `stdout_equals` (le texte du prompt `input("...")` se retrouve dans la
  sortie). Prefere `stdout_contains` ou `stdout_matches`.
- Pour `complete`, ajoute `source_not_contains` avec `"____"`.
- Pour forcer une notion (`for`, `while`, `def`, `super()`), utilise
  `source_contains`.

## Securite

Le code des exercices importes est **potentiellement dangereux**. Il est
execute dans un processus separe, en mode isole (`python -I`), avec timeout et
sortie bornee. Ce n'est **pas** une sandbox complete : voir
[execution.md](execution.md).
