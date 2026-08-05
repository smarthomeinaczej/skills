# Smart Home Inaczej — skille dla Claude Code

Skille (agent skills) używane na kanale [Smart Home Inaczej](https://www.youtube.com/@smarthomeinaczej).
Każdy skill to podkatalog z plikiem `SKILL.md` — instalujesz tylko te, których potrzebujesz.

## Dostępne skille

| Skill | Co robi | Odcinek |
|---|---|---|
| [obwody](obwody/) | Wywiad o Twoim domu (pokój po pokoju) i kompletna lista obwodów elektrycznych smart home jako `obwody.csv` — z kodami obwodów i propozycjami kabli | *(wkrótce)* |

## Instalacja

Wymagany [Claude Code](https://claude.com/claude-code). Sklonuj repo i skopiuj wybrany skill:

```bash
git clone https://github.com/smarthomeinaczej/skills
cp -r skills/obwody ~/.claude/skills/
```

Potem w Claude Code wpisz `/obwody` — skill poprowadzi Cię przez resztę.

Chcesz mieć skill tylko w jednym projekcie? Zamiast do `~/.claude/skills/` skopiuj go do `.claude/skills/` w katalogu projektu.

## Ważne

Skille pomagają zaplanować instalację, ale ostateczne przekroje kabli i zgodność
z przepisami zawsze potwierdza elektryk z uprawnieniami.

## Licencja

[MIT](LICENSE)
