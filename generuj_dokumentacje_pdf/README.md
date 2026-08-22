# generuj_dokumentacje_pdf

Skrypt `rozdzielnica_pdf.py` łączy wyniki skilli **[`obwody`](https://github.com/smarthomeinaczej/skills/tree/main/obwody)** i **[`rozdzielnica`](https://github.com/smarthomeinaczej/skills/tree/main/rozdzielnica)** w jeden PDF:

1. strona podsumowania — liczba obwodów (łącznie, per punkt zbiorczy, per typ) i bilans modułów obudowy,
2. tabela obwodów pogrupowana po pomieszczeniach (kolor wiersza = rozdzielnica / centrala alarmowa / szafa rack),
3. poglądowy rysunek rozdzielnicy — rzędy szyn DIN, bloki aparatów w kolorach grup różnicówkowych, pola `WOLNE`,
4. tabela rozkładu rzędów i zestawienie aparatów (sztuki per grupa).

## Wymagania

Tylko [`uv`](https://docs.astral.sh/uv/). Zależności (reportlab) są zadeklarowane w nagłówku PEP 723 skryptu — `uv run` pobiera je sam do izolowanego środowiska, nic nie instaluje się w systemie.

Do polskich znaków potrzebny jest font TTF (Noto Sans, DejaVu Sans lub Liberation Sans) w systemowym katalogu fontów; bez niego skrypt ostrzeże i użyje Helvetica.

## Pliki wejściowe

| Plik | Skąd | Nagłówek |
|---|---|---|
| `obwody.csv` | skill `obwody` | `kod,kondygnacja,pomieszczenie,typ,cel,opis,kabel,uwagi` |
| `moduly.csv` | skill `rozdzielnica`, Faza 4 | `rzad,pozycja_od,pozycja_do,aparat,grupa,ilosc,moduly` |

## Użycie

```bash
uv run rozdzielnica_pdf.py
```

Bez argumentów skrypt bierze `obwody.csv` i `moduly.csv` z **bieżącego katalogu** i zapisuje `projekt_instalacji.pdf` obok nich. Gdy któregoś pliku brakuje, kończy się komunikatem błędu z nazwą pliku i skillem, który go generuje.

Opcje:

| Opcja | Domyślnie | Opis |
|---|---|---|
| `--obwody` | `obwody.csv` | ścieżka do listy obwodów |
| `--moduly` | `moduly.csv` | ścieżka do rozkładu aparatów |
| `--out` | `projekt_instalacji.pdf` | plik wyjściowy |
| `--tytul` | `Projekt instalacji smart home` | tytuł na stronie głównej i w stopce |
| `--moduly-w-rzedzie` | max `pozycja_do` z `moduly.csv` | liczba modułów w rzędzie obudowy |

Przykład na danych demo z repo:

```bash
uv run rozdzielnica_pdf.py --obwody ../demo/obwody.csv --moduly moduly.csv --tytul "Dom demo"
```

## Zawartość folderu

- `rozdzielnica_pdf.py` — skrypt.

Projekt jest poglądowy — weryfikuje go elektryk z uprawnieniami.

