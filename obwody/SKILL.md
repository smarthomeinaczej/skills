---
name: obwody
description: Przeprowadza wywiad o Twoim domu (pokój po pokoju) i buduje kompletną listę obwodów elektrycznych smart home jako obwody.csv — z kodami obwodów i propozycjami kabli.
---

# Skill: obwody — wywiad → lista obwodów

Tworzysz listę obwodów elektrycznych dla domu w topologii gwiazdy. Kable schodzą się w trzech punktach zbiorczych: **rozdzielnica** (zasilanie i automatyka), **centrala alarmowa** (czujniki alarmowe) i **szafa rack** (sieć i multimedia). O tym, dokąd biegnie kabel, decyduje typ obwodu.
Prowadzisz wywiad z użytkownikiem **jedno pomieszczenie na raz**, a na końcu zapisujesz wynik do `obwody.csv`.

## Zasady nadrzędne

1. **Nie wymyślaj — pytaj.** Każdy obwód w CSV musi wynikać z odpowiedzi użytkownika albo z zaakceptowanego przez niego szablonu.
2. **Na starcie sprawdź istniejące pliki**, żeby nie zaczynać od zera:
   - jest `obwody.csv` — lista jest już gotowa; powiedz to użytkownikowi i zapytaj (AskUserQuestion), czy chce nanieść poprawki, czy zacząć od nowa,
   - jest tylko `pomieszczenia.csv` — pomiń Fazę A: pokaż zapisaną mapę domu i po potwierdzeniu przejdź do Fazy A2 (profil domu nie jest nigdzie zapisywany, więc te pytania trzeba zadać ponownie),
   - nie ma żadnego — zacznij od Fazy A.
3. **Jedno pytanie na raz.** Do pytań z ograniczoną liczbą opcji używaj AskUserQuestion; do otwartych — zwykłej rozmowy.
4. Na końcu przypomnij: *ostateczne przekroje kabli i zgodność z przepisami potwierdza elektryk z uprawnieniami.*

## System kodowania obwodów

Kod obwodu = `MIEJSCE-TYP{NUMER}` (+ opcjonalnie `-URZĄDZENIE`) — MIEJSCE i TYP rozdzielone myślnikiem; NUMER tylko wtedy, gdy w pomieszczeniu jest więcej obwodów tego samego typu.

**MIEJSCE (dwa znaki):**
- pierwszy znak — kondygnacja: `0` parter, `1` piętro, `Z` zewnątrz,
- drugi znak — numer pomieszczenia: zaczynając od wejścia, dalej **zgodnie ze wskazówkami zegara** (np. `01` wiatrołap, `02` kuchnia, `03` salon),
- powyżej dziewięciu pomieszczeń na kondygnacji kontynuuj literami: `0A` — dziesiąte, `0B` — jedenaste itd. (kod MIEJSCE zawsze zostaje dwuznakowy).

**TYP obwodu:**

| Skrót | Znaczenie | Proponowany kabel | Punkt zbiorczy |
|---|---|---|---|
| WL | włącznik (sygnał, bez 230 V) | skrętka U/UTP kat. 6 | rozdzielnica |
| OSW | oświetlenie 230 V | YDYp 3x1.5 | rozdzielnica |
| GN | gniazdka | YDYp 3x2.5 | rozdzielnica |
| ZAL | żaluzje / rolety | OWY 5x0.75 (silnik sterowany z rozdzielnicy) | rozdzielnica |
| 3F | obwód trójfazowy (np. indukcja) | YDYp 5x2.5 lub 5x4 | rozdzielnica |
| LAN | sieć / punkt dostępowy | skrętka U/UTP kat. 6 | szafa rack |
| KAM | kamera (PoE) | skrętka U/UTP kat. 6 | szafa rack |
| GLO | głośnik | kabel głośnikowy 2x1.5 | szafa rack |
| PIR | czujnik ruchu | YTDY 6x0.5 lub skrętka | centrala alarmowa |
| OBEC | czujnik obecności | YTDY 6x0.5 lub skrętka | rozdzielnica |
| KON | kontaktron okna/drzwi | YTDY 4x0.5 (alarmowy) | centrala alarmowa |
| DYM | czujnik dymu | YTDY 6x0.5 | centrala alarmowa |
| CZAD | czujnik czadu | YTDY 6x0.5 | centrala alarmowa |
| WOD | czujnik zalania | YTDY 4x0.5 | centrala alarmowa |

Wymiary kabli zapisuj zawsze w konwencji `3x1.5` (mała litera `x`, kropka dziesiętna) — bez znaku `×` i bez przecinka dziesiętnego, który rozjechałby kolumny CSV.

Gdy w pomieszczeniu jest więcej obwodów tego samego typu, dodaj numer po typie: `02-WL1`, `02-WL2`.
W kolumnie `typ` w CSV zawsze wpisuj pojedynczy skrót z tabeli (np. `PIR`, nie `PIR/OBEC`).

Przykłady: `02-WL1` — pierwszy włącznik w kuchni, `12-ZAL` — żaluzje w sypialni na piętrze, `02-GN-LOD` — gniazdko lodówki, `Z1-KAM` — kamera przy furtce.

## Format obwody.csv

Nagłówek (zawsze dokładnie taki):

```csv
kod,kondygnacja,pomieszczenie,typ,cel,opis,kabel,uwagi
```

Wartości kolumny `kondygnacja`: `parter`, `piętro`, `zewnątrz`.

Kolumna `cel` to punkt zbiorczy, do którego biegnie kabel — zawsze wartość z tabeli typów: `rozdzielnica`, `centrala alarmowa` albo `szafa rack`.

Wiersze zapisuj w kolejności pomieszczeń z `pomieszczenia.csv`.

Zapisuj plik w UTF-8. Pole zawierające przecinek ujmij w cudzysłowy (RFC 4180), np. `"oświetlenie blatu, wyspy i szafek"` — inaczej rozjedzie kolumny.

Przykładowy wiersz: `02-GN-LOD,parter,kuchnia,GN,rozdzielnica,gniazdko dedykowane lodówka,YDYp 3x2.5,obwód dedykowany`

## Proces wywiadu

### Faza A — mapa domu

1. Zapytaj (AskUserQuestion) o typ domu — **dokładnie dwie opcje, żadnych innych**: `parter` albo `parter + piętro`.
2. Zapytaj, czy jest strefa zewnętrzna (brama, furtka, ogród, elewacja).
3. Poproś o wyliczenie pomieszczeń na każdej kondygnacji (od wejścia, zgodnie ze wskazówkami zegara — na piętrze zacznij od schodów; pomóż użytkownikowi, jeżeli poda w innej kolejności).
4. Pokaż proponowaną numerację wszystkich pomieszczeń w tabeli i **czekaj na akceptację** przed przejściem dalej.
5. Po akceptacji zapisz mapę domu do `pomieszczenia.csv` z nagłówkiem:

```csv
miejsce,kondygnacja,pomieszczenie
```

Przykładowy wiersz: `02,parter,kuchnia` (kolumna `miejsce` = dwuznakowy kod MIEJSCE z systemu kodowania).

### Faza A2 — profil domu

Po zapisaniu mapy domu, a przed pierwszym pokojem, ustal globalne decyzje wpływające na szablony wielu pomieszczeń. Zadaj przez AskUserQuestion:

1. „Które z tych systemów planujesz w domu?" (multiSelect) — opcje: rolety/żaluzje sterowane, system alarmowy, audio multiroom (głośniki sufitowe), monitoring (kamery).
2. Tylko jeżeli wybrano system alarmowy: „Kontaktrony we wszystkich oknach czy tylko w drzwiach?" — opcje: wszystkie okna i drzwi / tylko drzwi.

Zapamiętaj odpowiedzi jako **profil domu** i stosuj go w Fazie B:

- brak rolet → nigdzie nie proponuj `ZAL`,
- brak alarmu → nie proponuj żadnych czujek alarmowych: ani `PIR`, ani `KON`, ani `DYM`, `CZAD` czy `WOD`,
- audio multiroom → proponuj `GLO` także w kuchni, łazience i na tarasie,
- brak monitoringu → nie proponuj `KAM`,
- kontaktrony we wszystkich oknach → dodaj `KON` do każdego pomieszczenia z oknem; w przeciwnym razie tylko drzwi wejściowe/tarasowe i brama.

### Faza B — pokój po pokoju

Dla każdego pomieszczenia po kolei:

1. Zaproponuj szablon obwodów według typu pomieszczenia (tabela niżej), **dostosowany do profilu domu z Fazy A2**. **Zawsze najpierw wyświetl pełną zawartość szablonu** — tabelę z proponowanymi obwodami (typ, opis, kabel) — i dopiero potem zapytaj: co dodać, co usunąć, co zmienić? Nigdy nie pytaj o akceptację szablonu, którego użytkownik nie widzi na ekranie.
2. Dopytaj o rzeczy nieoczywiste: obwody dedykowane AGD, liczba włączników, czujniki, głośniki sufitowe.
3. Po akceptacji zapamiętaj obwody pomieszczenia i przejdź do następnego.

**Szablony pomieszczeń (punkt startowy rozmowy, nie dogmat):**

| Pomieszczenie | Typowy zestaw |
|---|---|
| wiatrołap | WL, OSW, GN, KON (drzwi), KAM (opcja) |
| kuchnia | WL×2, OSW, GN×3, GN-LOD, GN-ZMY, GN-PIE, 3F (indukcja), ZAL, KON, DYM |
| salon | WL×2, OSW, GN×4, ZAL (na okno), GLO, OBEC |
| sypialnia | WL×2 (przy łóżku), OSW, GN×3, ZAL, KON |
| pokój dziecka | jak sypialnia |
| łazienka | WL, OSW, GN×2, OBEC, WOD |
| korytarz / schody | WL×2, OSW, OBEC×2, DYM |
| biuro | WL, OSW, GN×4, LAN×2, ZAL |
| garaż | WL, OSW, GN×2, GN 3F (opcja warsztat/wallbox), KON (brama), CZAD |
| pom. techniczne | WL, OSW, GN×2, LAN (uplink), DYM, WOD |
| zewnętrze | OSW (elewacja), GN (taras), KAM, KON (furtka/brama), LAN (bramofon) |

### Zakończenie

1. Pokaż podsumowanie: liczba obwodów łącznie, per typ i per punkt zbiorczy (rozdzielnica / centrala alarmowa / szafa rack).
2. Zwaliduj listę przed zapisem:
   - każdy `kod` jest unikalny,
   - prefiks MIEJSCE każdego kodu istnieje w `pomieszczenia.csv`,
   - każdy `typ` pochodzi z tabeli typów,
   - `cel` zgadza się z punktem zbiorczym danego typu z tabeli typów,
   - każdy wiersz ma dokładnie 8 kolumn.
   Znalezione błędy popraw przed zapisem — nie zapisuj pliku z błędami.
3. Zapisz finalny `obwody.csv` i podaj ścieżkę.
4. Powiedz, że następny krok to skill `rozdzielnica`, który na podstawie tego pliku dobierze aparaty i policzy wielkość rozdzielnicy.
