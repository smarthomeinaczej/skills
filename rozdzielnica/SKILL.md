---
name: rozdzielnica
description: Na podstawie obwody.csv i kilku pytań o instalację dobiera aparaty do rozdzielnicy smart home i buduje zestawienie zakupowe — ile różnicówek, esek i pozostałych aparatów kupić.
---

# Skill: rozdzielnica — obwody.csv → dobór aparatów

Zamieniasz listę obwodów w poglądowy projekt rozdzielnicy: grupy różnicówkowe, przypisanie obwodów do faz, bilans modułów i **konkretne zestawienie zakupowe — ile różnicówek, esek i pozostałych aparatów kupić**.

## Zasady nadrzędne

1. **Wejściem jest `obwody.csv`** (format ze skilla `obwody`: kolumny `kod,kondygnacja,pomieszczenie,typ,cel,opis,kabel,uwagi`). Zapytaj o ścieżkę, domyślnie szukaj w bieżącym katalogu. Bez tego pliku nie zgaduj — zaproponuj najpierw skill `obwody`.
2. **Ustalenia przed doborem.** Każda decyzja projektowa musi paść w rozmowie — używaj AskUserQuestion. Faza 1 to *tylko pytania*; wszystkie konsekwencje odpowiedzi są opisane w Fazie 2 (jedno źródło prawdy).
3. Wynik jest **poglądowy**: w podsumowaniu zawsze zaznacz, że projekt wymaga weryfikacji elektryka z uprawnieniami i zgodności z aktualnymi normami.

## Faza 1 — ustalenia wstępne

Zadaj pytania w czterech pakietach (AskUserQuestion przyjmuje do 4 pytań naraz); pytania zależne zadaj w kolejnym kroku.

**Pakiet A — przyłącze**

1. **Moc przyłączeniowa i liczba faz** — moc z umowy z OSD i zabezpieczenie przedlicznikowe (typowo 3×25 A ≈ 17 kW)? Instalacja trójfazowa czy jednofazowa?
2. **Układ sieci** — jaki układ jest **potwierdzony w warunkach przyłączenia, dokumentacji lub przez elektryka**: TN-C, TN-S, TN-C-S, TT czy nieznany? **Nie ustalaj układu wyłącznie na podstawie liczby żył** — 4 żyły co najwyżej sugerują PEN, TT bywa zasilane czterema żyłami, a piąta żyła nie dowodzi, że PE jest poprawnie uziemiony po stronie OSD.
3. **Ogranicznik przepięć** — dodać SPD T1+T2? (rekomendacja: tak — w smart home elektronika jest w każdej puszce).
4. **Producent aparatury** — pokaż opcje z `aparaty_katalog.csv` (Hager, Eaton, Schneider Electric, Legrand, Noark) + "bez preferencji". Mieszanie marek jest technicznie OK, ale jedna rodzina upraszcza montaż i estetykę.

**Pakiet B — duże odbiorniki i źródła** (każda odpowiedź "tak" → dopytaj o szczegóły w kolejnym kroku)

5. **Źródło ciepła** — pompa ciepła / kocioł gazowy-olejowy / kocioł na pellet lub kominek z płaszczem wodnym / ogrzewanie elektryczne / brak lub jeszcze nieustalone. Dopytaj: pompa ciepła — 1F czy 3F, moc [kW]; ogrzewanie elektryczne — liczba i moc obwodów grzewczych.
6. **Fotowoltaika i magazyn energii** — jest lub będzie? Dopytaj: moc i liczba faz falownika, czy stoi przy rozdzielnicy, czy ma wbudowaną detekcję prądu stałego (RCMU — z DTR), czy jest magazyn, czy przewidziana praca awaryjna (backup / wyspa) i **które obwody mają być podtrzymywane**.
7. **Wallbox** — jest lub będzie? Dopytaj: moc i fazy (11 kW/3F, 22 kW/3F, 7,4 kW/1F), **czy ma wbudowane wykrywanie 6 mA DC** (z DTR), czy ma mieć **zarządzanie mocą / dynamiczne ograniczanie prądu**.
8. **Podliczniki** — czy mierzyć energię osobno dla wybranych grup (źródło ciepła, PV, wallbox, cały dom)? Opcje: brak / tylko licznik na wejściu / wejście + podliczniki wybranych grup.

**Pakiet C — sterowanie**

9. **System sterowania** — opcje z `sterowniki_katalog.csv` (boneIO, SmartBob, nippy, Shelly Pro) + "klasyczne przekaźniki modułowe" + "inne". Zaznacz różnice: boneIO/SmartBob = duże sterowniki ESPHome z wbudowanymi wejściami (bez bramki), nippy = drobne moduły na magistrali (wymaga bramki Gateway), Shelly Pro = moduły per funkcja z lokalnym API (bez bramki, **włączniki pod 230 V**).
10. **Zakończenie skrętek od włączników (WL)** — zadaj tylko, gdy system ma wejścia niskonapięciowe (boneIO, SmartBob, nippy). Opcje: (a) **patch panel krosowy** + krosówki do wejść, (b) **moduły wejściowe z gniazdami RJ45** (np. EasySwitch GPIO DIN) bez patch panelu, (c) **bezpośrednio na zaciski wejść** — najtaniej, mniej czytelne. Moduły RJ45 działają w (a) i (b); są **poza `sterowniki_katalog.csv`** — dostępność i parametry potwierdź u producenta.
11. **Zasilacze LED** — centralnie w rozdzielnicy czy lokalnie przy taśmach?

**Pakiet D — obudowa**

12. **Obudowa rozdzielnicy** — już kupiona? Jeśli tak: liczba rzędów i modułów w rzędzie (albo łączna liczba modułów). Jeśli nie — skill zaproponuje wielkość po bilansie.

## Faza 2 — reguły doboru aparatów

### 2.1 Konsekwencje ustaleń z Fazy 1

**Liczba faz.** 3F → rozłącznik główny 4P, lampka obecności faz. 1F → rozłącznik 2P, bez lampki; obwody `typ=3F` z `obwody.csv` wypisz jako wymagające wyjaśnienia z użytkownikiem. Prąd znamionowy rozłącznika: najbliższy nie mniejszy niż zabezpieczenie przedlicznikowe.

**Układ sieci.**
- **TN-C (PEN do rozdzielnicy)** — powiedz wprost, że **PEN trzeba rozdzielić na PE i N**; bez tego różnicówki nie zadziałają. Rozdział **raz** — w złączu albo na wejściu rozdzielnicy; za punktem rozdziału PE i N nigdy się nie łączą; do punktu rozdziału przyłączone uziemienie; PEN ≥ 10 mm² Cu (16 mm² Al). Do zestawienia: **mostek PEN→PE** (szyny PE i N zwykle w komplecie z obudową — zaznacz). Praca dla elektryka z uprawnieniami.
- **TN-C-S** — rozdział w złączu; do rozdzielnicy przychodzą osobne PE i N. Potwierdź, **gdzie** jest punkt rozdziału i czy jest uziemiony; za nim nie łączyć PE z N.
- **TN-S** — osobne PE i N od źródła; bez mostka.
- **TT** — ochronę realizują **różnicówki** (obowiązkowe na wszystkich obwodach) w oparciu o **własny uziom** — zaznacz, że rezystancję uziomu trzeba zmierzyć. SPD w konfiguracji **3+1** (iskiernik N-PE) albo za różnicówką — pozycja do weryfikacji z elektrykiem.
- **Nieznany** — dobór wejścia i SPD oznacz **TBD — wymaga potwierdzenia układu sieci** (w zestawieniu i raporcie), zarezerwuj moduły wg wariantu najszerszego, nie przesądzaj konfiguracji SPD ani rozdziału PEN. Resztę projektu prowadź normalnie.

**Źródło ciepła.**
- pompa ciepła — osobna różnicówka typu A + eska C16/3 (1F: C16 1P) + rozłącznik izolacyjny (wymóg większości producentów); przy pompie z falownikiem sprawdź w DTR, czy nie wymaga RCD typu B,
- kocioł / kominek z płaszczem — dedykowany obwód 1F na automatykę i pompy obiegowe: B10 1P, bez współdzielenia z gniazdkami,
- ogrzewanie elektryczne — każdy obwód grzewczy własna eska wg mocy (typowo B16 1P lub B16/3), osobna różnicówka,
- nieustalone — rezerwa modułów i osobno wyprowadzony obwód.

**Fotowoltaika i magazyn.**
- obwód AC falownika: eska wg DTR (typowo B16/3 przy 3F, B20 1P przy 1F) + różnicówka — **typ A tylko gdy falownik ma wbudowaną detekcję DC (RCMU); inaczej typ B** — zawsze sprawdź DTR,
- falownik poza rozdzielnicą → obwód AC wychodzi z tej rozdzielnicy do podrozdzielnicy falownika (ta sama eska/RCD),
- licznik dwukierunkowy / CT na wejściu instalacji (zwykle dostawa instalatora — zarezerwuj 2–5 modułów i trasę kabla komunikacyjnego),
- SPD DC montuje się przy falowniku, nie tu,
- magazyn energii: osobny obwód, eska wg DTR + rozłącznik izolacyjny,
- praca awaryjna: obwody podtrzymywane trafiają do **osobnej sekcji backup** zasilanej z wyjścia backup falownika — osobna różnicówka; jeśli falownik nie ma automatycznego przełączania, dolicz **przełącznik źródła I-0-II 4P** (`przelacznik_zrodla_I-0-II_4P` z katalogu) w rzędzie wejścia; uwzględnij sekcję w rozkładzie rzędów,
- PV nie ma i nie będzie — sama rezerwa modułów i trasa kablowa.

**Wallbox.** Własny obwód, osobna różnicówka: **typ B (albo B-EV / G/B), gdy ładowarka nie ma detekcji 6 mA DC; typ A tylko, gdy DTR wprost na to pozwala**; eska wg DTR (typowo B16/3 przy 11 kW, B32/3 przy 22 kW). Zarządzanie mocą wymaga licznika/CT na wejściu (to samo miejsce co przy PV). Pozycja specjalna w raporcie; różnicówki typ B są drogie i szerokie — zaznacz. Planowany, ale nie kupiony → rezerwa modułów i wyprowadzenie kabla.

**Podliczniki.** Licznik na wejściu → `licznik_energii_3F_modbus` (lub dwukierunkowy/CT, gdy jest PV/wallbox). Podliczniki grup → po jednym liczniku na grupę z ustaleń (przy Shelly Pro można użyć `energy` ze `sterowniki_katalog.csv`). Ostrzeż, gdy licznik ma `pomiar=CT` (wymaga przekładników) lub `MID=0` (nie do rozliczeń).

**System sterowania — Shelly Pro.** Wejścia S1–S4 są pod **230 V**, więc obwody `WL` na skrętce z `obwody.csv` są wtedy **niepoprawne**: włączniki trzeba prowadzić YDY 3x1.5 do rozdzielnicy (albo montować moduły w puszkach). Powiedz to wprost, zaproponuj powrót do skilla `obwody` i poprawę kabli, a w tym projekcie nie licz WL do strefy niskonapięciowej.

### 2.2 Bilans mocy

Policz **przed** doborem grup i zapisz w ustaleniach:

- moc przyłączeniowa P_przył z pytania 1 (3×25 A → 17 kW, 3×32 A → 22 kW, 3×40 A → 27 kW, 1×25 A → 5,5 kW),
- sumuj duże odbiorniki: płyta indukcyjna (`typ=3F` z opisem indukcja; domyślnie 7 kW), pompa ciepła (moc z ustaleń; gdy nieznana 3 kW 1F / 6 kW 3F), obwody grzewcze elektryczne (moc z ustaleń), wallbox (11 / 22 / 7,4 kW), pozostałe AGD i gniazdka ryczałtem 4 kW, oświetlenie i automatyka 1 kW,
- moc szczytowa = suma × współczynnik jednoczesności **0,7** (bez wallboxa) albo **0,8** (z wallboxem, bo ładowanie jest długie i nocne razem z PC),
- **werdykt**: moc szczytowa ≤ P_przył → OK; 100–120 % → ostrzeż i zaproponuj zarządzanie mocą wallboxa (dynamiczne ograniczanie z CT) lub ograniczenie PC; > 120 % → powiedz wprost, że potrzebny jest wniosek do OSD o zwiększenie mocy przyłączeniowej albo rezygnacja z części odbiorników. Werdykt trafia do raportu.

### 2.3 Mapowanie obwodów na grupy

Przypisuj grupy na podstawie kolumn `typ`, `kondygnacja`, `cel` i słów kluczowych w `opis`/`uwagi` (wielkość liter bez znaczenia). **Nie oczekuj kodów typu `GN-LOD`** — skill `obwody` wpisuje w `typ` pojedynczy skrót, a urządzenie siedzi w `opis`. Kolejność sprawdzania = kolejność wierszy (pierwsze dopasowanie wygrywa):

| Warunek | Grupa | Eska |
|---|---|---|
| `cel` ≠ `rozdzielnica` | poza zakresem (szafa rack / centrala alarmowa) — tylko informacyjnie | — |
| `typ` ∈ {WL, KON, OBEC, PIR, DYM, CZAD, WOD} i pozostałe sygnałowe | strefa niskonapięciowa (WL) lub poza zakresem | — |
| `kondygnacja` = `zewnątrz` | **ogród/zewnętrze** | OSW → B10 1P, GN → B16 1P |
| `typ` = 3F, opis: indukcja \| płyta \| piekarnik | **AGD 3F** | B16/3 |
| `typ` = 3F, opis: pompa ciepła | **źródło ciepła** | C16/3 + rozłącznik izolacyjny |
| `typ` = 3F, opis: wallbox \| ładowarka | **wallbox** | wg DTR (B16/3 / B32/3) |
| `typ` = 3F, opis: falownik \| PV | **PV / magazyn** | wg DTR (B16/3) |
| `typ` = 3F, inne (warsztat, rezerwa) | **AGD 3F** | B16/3 lub C16/3 |
| `typ` = GN, opis: lodówka \| zamrażarka \| zmywarka \| piekarnik \| pralka \| suszarka \| okap \| mikrofala \| ekspres \| kuchenka | **AGD dedykowane** | B16 1P |
| `typ` = GN, opis: kocioł \| kominek \| pompa obiegowa \| automatyka kotła \| rekuperator \| kotłownia | **źródło ciepła** | B10 1P |
| `typ` = GN, opis: falownik \| magazyn \| wallbox | odpowiednio PV / wallbox | wg DTR |
| `typ` = OSW | **oświetlenie** | B10 1P (C10, gdy na obwodzie > 3 zasilaczy LED — prąd rozruchowy) |
| `typ` = LED (zasilacz taśmy) | **oświetlenie** | B6 1P |
| `typ` = ZAL | **teletechnika/żaluzje** | B10 1P |
| `typ` = GN (reszta) | **gniazdka ogólne** | B16 1P |
| zasilacze sterowników / bramki (dodawane przez skill) | **teletechnika/żaluzje** | B6 1P |

Obwody, które nie pasują do żadnego wiersza, wypisz użytkownikowi i zapytaj o grupę — nie zgaduj.

### 2.4 Różnicówki

- Każda grupa → własna różnicówka **typu A**, 30 mA — **nigdy AC**. Wyjątki: wallbox (typ B / B-EV wg 2.1), falownik PV bez RCMU (typ B), pompa ciepła z falownikiem, jeśli DTR wymaga (typ B).
- **In różnicówki ≥ zabezpieczenie przedlicznikowe** (3×25 A → 40 A; 3×40 A lub więcej → 63 A). Katalog ma tylko 40 A — przy większym przyłączu dopisz pozycję "różnicówka 63 A — poza katalogiem, potwierdź symbol u producenta".
- **Max 5 esek na jedną różnicówkę** (większe grupy dziel). Powody: sumaryczny prąd upływu wielu odbiorników sam potrafi wyzwalać 30 mA, a jedno uszkodzenie gasi pół domu. Dziel grupę **per kondygnacja** (`parter` / `piętro`), a jeśli nadal > 5 esek — na dwie podgrupy w obrębie kondygnacji (np. "gniazdka parter 1", "gniazdka parter 2").
- **Oświetlenie nigdy na tej samej różnicówce co gniazdka** tej samej strefy — zwarcie w gniazdku nie może zgasić światła.
- Źródło ciepła, PV/magazyn, wallbox, ogród — zawsze osobne różnicówki, nigdy łączone z grupami domowymi.
- 4P dla grup trójfazowych i mieszanych (obwody rozdzielone na różne fazy), 2P dla małych grup jednofazowych na jednej fazie.

### 2.5 Rozdział faz

Przy instalacji 3F każdy obwód 1F dostaje fazę **L1 / L2 / L3**:

1. odbiorniki 3F (indukcja, PC, wallbox, falownik 3F) zajmują wszystkie fazy — nie liczą się do bilansu 1F,
2. duże odbiorniki 1F (PC 1F, obwody grzewcze, falownik 1F, wallbox 1F) przypisz najpierw, każdy na inną fazę, zaczynając od najmniej obciążonej,
3. pozostałe obwody rozkładaj **round-robin w obrębie każdej grupy różnicówkowej** (pierwsza eska grupy na L1, druga L2, trzecia L3, …), tak żeby każda grupa 4P miała obwody na wszystkich fazach, a sumaryczna liczba obwodów na fazę różniła się najwyżej o 1,
4. sprawdź sumę mocy szacunkowej per fazę (gniazdko 1 kW, AGD 2 kW, oświetlenie 0,3 kW, żaluzje 0,3 kW, obwód grzewczy wg mocy) — różnica między fazami nie większa niż ~30 %; jeśli jest, przełóż obwody AGD.

Przy instalacji 1F wszystkie obwody dostają `L1`.

### 2.6 Strefa niskonapięciowa

Obwody sygnałowe nie dostają aparatów zabezpieczeniowych. Do strefy trafiają tylko te z `cel=rozdzielnica` (przede wszystkim WL i sygnały sterowników). Obwody z `cel=szafa rack` (LAN, KAM) i `cel=centrala alarmowa` (PIR, OBEC, KON, DYM, CZAD, WOD) są **poza zakresem** — w raporcie tylko informacyjnie, bez doboru wyposażenia.

- **zakończenie WL** wg ustaleń: patch panel krosowy → "patch panel 24-portowy" (1 na każde rozpoczęte 24 porty WL — kros do wejść sterownika, nie switch) + "krosówki"; moduły RJ45 (np. EasySwitch GPIO DIN) → osobna pozycja z dopiskiem "poza katalogiem skilla — potwierdź dostępność i parametry u producenta"; bezpośrednio → listwy/złączki zaciskowe; Shelly Pro → nic (patrz 2.1),
- **sterowniki** — dobieraj ze `sterowniki_katalog.csv`, filtrując po systemie: sztuki = ⌈liczba obwodów danej funkcji ÷ `liczba_kanalow`⌉ (relay ← OSW, cover ← ZAL, dimmer_led ← LED, input ← WL); wejścia bywają wbudowane w sterowniki (`uwagi`); wiersz `gateway` z "wymagana" → dolicz bramkę; `szerokosc_moduly` do bilansu; pomijaj `status_produktu=EOL`, przy `preorder` ostrzeż,
- **zasilacze** — policz bilans DC: sterowniki, bramka, ekspandery (pobór z karty; brak danych → 10 W duży sterownik przekaźnikowy, 2 W mały moduł magistralowy); suma × 1,4 → najmniejszy wystarczający zasilacz z `aparaty_katalog.csv` (`Pout_W`/`Iout_A` w `parametry`; ostrzeż, gdy `Iout_A` za małe). Taśmy LED centralnie → osobny zasilacz per obwód LED (moc taśmy × 1,25; 12 lub 24 V wg taśmy; **nigdy wspólny ze sterownikami**), dolicz moduły i zaznacz kwestię ciepła (odstępy, wentylacja). Lokalnie → w rozdzielnicy tylko eski B6,
- listwy zaciskowe przy żaluzjach sterowanych z rozdzielnicy.

### 2.7 Wejście rozdzielnicy

| Aparat | Warunek |
|---|---|
| rozłącznik główny 4P (3F) / 2P (1F) | zawsze; In ≥ zabezpieczenie przedlicznikowe |
| mostek PEN→PE | tylko TN-C (szyny PE i N są potrzebne w każdym układzie — zwykle w komplecie z obudową) |
| SPD T1+T2 | jeśli wybrano; konfiguracja wg układu sieci (TT: 3+1 lub za różnicówką; nieznany: TBD) |
| licznik energii 3F (dwukierunkowy + CT przy PV / wallboxie z zarządzaniem mocą) | jeśli PV, wallbox z zarządzaniem mocą albo podlicznik "wejście" z ustaleń |
| przełącznik źródła I-0-II 4P | tylko backup PV bez automatycznego przełączania w falowniku |
| lampka obecności faz | przy instalacji 3F |

### 2.8 Bilans modułów DIN

Szerokości bierz z `aparaty_katalog.csv` — filtruj po producencie z ustaleń, wiersze `generic` jako fallback (to rezerwa projektowa = maksimum z katalogu, nie szerokość konkretnego produktu). Pomijaj `status_produktu=EOL` i `brak`; przy `do_weryfikacji` poinformuj użytkownika. Gdy pliku brakuje:

| Aparat | Moduły |
|---|---|
| rozłącznik główny 4P / 2P | 4 / 2 |
| SPD T1+T2 | 4–8 (Hager 8) |
| licznik energii 3F | 4–5 |
| przełącznik źródła I-0-II 4P | 4–8 |
| lampka obecności faz | 1 |
| różnicówka 4P / 2P (typ A) | 4 / 2 |
| różnicówka 4P typ B / B-EV | 4 (bywa 6) |
| eska 1P / 3P | 1 / 3 |
| rozłącznik izolacyjny 3P | 3 |
| zasilacz DIN | 2–6 (wg mocy) |
| sterowniki/przekaźniki | wg `sterowniki_katalog.csv` |

Do sumy dolicz **min. 20–30 % rezerwy**. Następnie: obudowa kupiona → porównaj z pojemnością; nie mieści się albo rezerwa < 20 % → powiedz wprost i zaproponuj większą. Obudowy nie ma → zaproponuj najbliższy typowy rozmiar (rzędy × moduły, np. 4×24); podtynkowa/natynkowa — decyzja użytkownika.

## Faza 3 — przypisanie obwodów i zestawienie zakupowe

Zapisz dwa pliki.

**`obwody_zabezpieczenia.csv`** — każdy obwód 230 V z `obwody.csv` jeden wiersz:

```csv
kod,grupa,roznicowka,eska,faza
```

`roznicowka` = identyfikator grupy (np. `RCD-OSW-P` oświetlenie parter, `RCD-GN-P1`, `RCD-PC`, `RCD-EV`), `eska` = np. `B16 1P`, `faza` = `L1`/`L2`/`L3`/`L123`. Obwody poza rozdzielnicą (rack, centrala) tu nie wchodzą.

**`aparaty.csv`** — zestawienie zakupowe:

```csv
aparat,producent,symbol,grupa,ilosc,moduly_szt
```

`aparat` = nazwa z kolumny `aparat` katalogu (lub opis dla pozycji poza katalogiem), `producent`/`symbol` z katalogu (puste + dopisek w `aparat`, gdy brak), `moduly_szt` = szerokość jednej sztuki. Pozycje TBD i "poza katalogiem" zaznaczaj w nazwie aparatu. Ten plik jest wejściem do Fazy 4 i do wyceny.

## Faza 4 — rozkład aparatów w rzędach

Rozłóż aparaty z `aparaty.csv` na rzędy obudowy i zapisz `moduly.csv`:

```csv
rzad,pozycja_od,pozycja_do,aparat,grupa,ilosc,moduly
```

`moduly` = `pozycja_do - pozycja_od + 1`. Aparaty tego samego typu w tej samej grupie jednym wierszem (9 esek B10 → `ilosc=9`, `moduly=9`).

Kolejność:

1. **Rząd 1 — wejście:** rozłącznik główny, mostek PEN (TN-C), SPD, licznik, przełącznik źródła, lampka obecności faz.
2. **Kolejne rzędy — grupy 230 V:** każda grupa zaczyna się od różnicówki, za nią jej eski. Kolejność: oświetlenie, gniazdka ogólne, AGD, teletechnika/żaluzje, źródło ciepła, PV/magazyn (+ sekcja backup), wallbox, ogród.
3. **Ostatnie rzędy — strefa niskonapięciowa:** sterowniki, ekspandery, bramka, zasilacze, patch panele. **Nie mieszaj ich w jednym rzędzie z aparatami 230 V.**

Zasady:

- **Grupy różnicówkowej nie dziel między rzędy** — nie mieści się → cała do następnego rzędu, reszta bieżącego jako `WOLNE`.
- Każdy niewykorzystany fragment rzędu → `aparat=WOLNE`, `grupa=rezerwa`.
- Rezerwę **rozprosz** (koniec rzędu z gniazdkami, strefa niskonapięciowa), nie jednym blokiem na końcu.
- Zasilacze i sterowniki grzeją — raczej na końcu rzędu.
- Nie mieści się → **nie zmniejszaj rezerwy poniżej 20 %** — powiedz wprost i wróć do rekomendacji obudowy z 2.8.

## Faza 5 — raport

Zapisz `rozdzielnica_projekt.md`:

1. podsumowanie ustaleń z Fazy 1,
2. **bilans mocy** (2.2) z werdyktem,
3. grupy różnicówkowe z przypisanymi obwodami i fazami (ten sam układ co `obwody_zabezpieczenia.csv`) + tabela obciążenia per faza,
4. **bilans modułów**: ile zajmuje projekt, ile rezerwy, werdykt obudowy; **rozkład rzędów w tabeli** (jak `moduly.csv`),
5. **zestawienie zakupowe: tabela aparat / symbol / ile sztuk per grupa** — główny wynik skilla,
6. pozycje specjalne: rozdział PEN (TN-C/TN-C-S), TT — pomiar uziomu i SPD 3+1, układ nieznany — pozycje TBD, pompa ciepła — rozłącznik izolacyjny i typ RCD wg DTR, PV — typ RCD wg DTR, licznik/CT, obwody podtrzymywane i przełącznik źródła, wallbox — RCD typ B/B-EV i zarządzanie mocą, Shelly Pro — włączniki pod 230 V (poprawa `obwody.csv`), różnicówki 63 A poza katalogiem; oraz informacyjna lista obwodów poza rozdzielnicą (szafa rack, centrala alarmowa),
7. disclaimer: projekt poglądowy do weryfikacji przez elektryka z uprawnieniami.

