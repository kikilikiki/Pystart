# Contribuer a Pystart

Merci de vouloir aider ! Pystart vise a rester **simple, pedagogique, sur et
maintenable**.

## Avant de commencer

- Ouvre une *issue* pour discuter d'un changement important.
- Pour du contenu (cours, exercices), aucune connaissance de Qt n'est requise :
  voir [courses.md](courses.md) et [exercises.md](exercises.md).

## Mise en place

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Style

- **PEP 8**, verifie par `ruff check .`.
- Type hints sur les signatures publiques.
- Docstrings sur les classes et fonctions non triviales.
- Commentaires : expliquer le *pourquoi* et les concepts Python, pas paraphraser
  chaque ligne.
- Fonctions courtes, classes a responsabilite unique, pas de fichier geant.

## Commits

Format `type: resume` :

```
feat: add pygame course
fix: handle empty editor on verify
docs: clarify update security
test: add zip-bomb rejection test
release: v0.0.2
```

## Checklist avant une Pull Request

- [ ] `pytest` passe
- [ ] `ruff check .` ne remonte rien
- [ ] l'application se lance (`python -m app`) et la fonctionnalite marche
- [ ] doc mise a jour si besoin
- [ ] `CHANGELOG.md` : entree ajoutee sous « Non publie »
- [ ] aucun secret, aucune donnee perso commitee

## Securite

Signale toute faille en prive par e-mail : **pystartcontact@gmail.com**
(ne pas ouvrir d'issue publique pour une faille).
