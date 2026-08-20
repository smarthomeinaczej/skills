---
name: rozdzielnica
description: Na podstawie obwody.csv i krótkiego wywiadu decyzyjnego dobiera aparaty do rozdzielnicy smart home i buduje zestawienie zakupowe — ile różnicówek, esek i pozostałych aparatów kupić.
---

# Skill: rozdzielnica — obwody.csv → dobór aparatów

Zamieniasz listę obwodów w poglądowy projekt rozdzielnicy: sekcje, grupy różnicówkowe i **konkretne zestawienie zakupowe — ile różnicówek, esek i pozostałych aparatów kupić**.

## Zasady nadrzędne

1. **Wejściem jest `obwody.csv`** (format ze skilla `obwody`). Zapytaj o ścieżkę, domyślnie szukaj w bieżącym katalogu. Bez tego pliku nie zgaduj — zaproponuj najpierw skill `obwody`.
2. **Wywiad przed doborem.** Każda decyzja projektowa (SPD, licznik, pompa ciepła…) musi paść w rozmowie — używaj AskUserQuestion.
3. Wynik jest **poglądowy**: w podsumowaniu zawsze zaznacz, że projekt wymaga weryfikacji elektryka z uprawnieniami i zgodności z aktualnymi normami.

## Faza 1 — wywiad decyzyjny

Zadaj po kolei (jedno pytanie na raz):

1. **Producent aparatury** — jakiej marki mają być aparaty? Pokaż kilka opcji z `aparaty_katalog.csv` (np. Hager, Eaton, Schneider Electric, Legrand, Noark) + opcja "bez preferencji". Wybór wpływa na przykładowe serie w zestawieniu; mieszanie marek jest technicznie OK, ale zaznacz, że jedna rodzina upraszcza montaż i estetykę.
2. **Ogranicznik przepięć** — czy dodać SPD typ T1+T2? (rekomendacja: tak — w smart home elektronika jest w każdej puszce).
3. **Licznik energii** — czy dodać licznik z pomiarem per faza i wyjściem Modbus (integracja z Home Assistantem, gotowość na fotowoltaikę)? (rekomendacja: tak).
4. **Pompa ciepła** — jest lub będzie? (osobna różnicówka + eska C, rozłącznik izolacyjny — wymóg większości producentów).
5. **Wallbox / auto elektryczne** — planowany? (osobny obwód z RCD **typu B** — zaznacz w wynikach jako pozycję specjalną).
6. **System sterowania** — czym będą sterowane światła/żaluzje? Pokaż opcje z `sterowniki_katalog.csv` (boneIO, SmartBob, nippy, Shelly Pro) + "klasyczne przekaźniki modułowe" + "inne". Zaznacz różnice architektur: boneIO/SmartBob = duże sterowniki ESPHome z wbudowanymi wejściami (bez bramki), nippy = drobne moduły na magistrali (wymaga bramki Gateway), Shelly Pro = moduły per funkcja z lokalnym API (bez bramki). Wybór wpływa na wyposażenie strefy niskonapięciowej.
7. **Zakończenie skrętek od włączników (WL)** — zadaj tylko, gdy wybrany system sterowania ma wejścia niskonapięciowe (boneIO, SmartBob, nippy; przy Shelly Pro pomiń — włączniki podłącza się do wejść S1-S4 przy module, pod napięciem sieciowym). Opcje: (a) patch panel krosowy — WL na osobny patch panel, krosówki do wejść sterownika; porządek i łatwa diagnostyka kosztem dodatkowego panelu, (b) moduły wejściowe z RJ45 (np. EasySwitch GPIO DIN) — skrętka wpinana wprost; zaznacz, że to rozwiązanie DIY o ograniczonej dostępności, (c) bezpośrednio na zaciski wejść sterownika — najtaniej, mniej czytelne przy dużej liczbie kabli. Wybór decyduje, czy WL liczy się do patch paneli (patrz strefa niskonapięciowa).
8. **Zasilacze LED** — gdzie staną zasilacze taśm LED: centralnie w rozdzielnicy (doliczamy ich moduły i przekrój kabli DC) czy lokalnie przy taśmach (w rozdzielnicy tylko 230 V do zasilaczy)?
9. **Obudowa rozdzielnicy** — czy jest już kupiona? Jeśli tak — zapytaj o liczbę rzędów i modułów w rzędzie (albo łączną liczbę modułów) i na końcu zweryfikuj, czy projekt się w niej mieści. Jeśli nie — na podstawie bilansu modułów zaproponuj wielkość.

## Faza 2 — reguły doboru aparatów

**Wejście rozdzielnicy (zawsze):**

| Aparat | Warunek |
|---|---|
| rozłącznik główny (FR) 4P | zawsze |
| SPD T1+T2 | jeśli wybrano |
| licznik energii 3F | jeśli wybrano |
| lampka obecności faz | zawsze |

**Grupowanie obwodów 230 V w rodziny** (każda rodzina → własna różnicówka **typu A** — nigdy AC):

- oświetlenie (OSW, LED — zasilacze LED),
- gniazdka ogólne (GN),
- gniazdka AGD dedykowane (GN-LOD, GN-ZMY, GN-PIE…),
- teletechnika/żaluzje (ZAL + zasilacze sterowników),
- pompa ciepła (osobno),
- ogród/zewnętrze (osobno),
- wallbox (osobno, RCD typ B).

Różnicówka 4P dla grup trójfazowych i mieszanych, 2P dla małych grup jednofazowych.

**Eski — każda usługa na własnej esce:**

- obwód oświetleniowy → B10 1P,
- obwód gniazdkowy → B16 1P,
- AGD dedykowane → B16 1P,
- obwód 3F → B16/3 lub C16/3,
- zasilacz automatyki/LED → B6 1P,
- pompa ciepła → C16/3 + rozłącznik izolacyjny.

**Obwody sygnałowe:** nie dostają aparatów zabezpieczeniowych. Do strefy niskonapięciowej rozdzielnicy trafiają tylko te z przeznaczeniem "rozdzielnica" (przede wszystkim WL i sygnały sterowników). Obwody z przeznaczeniem "szafa rack" (LAN, KAM) i "centrala alarmowa" (PIR, OBEC, CON, DYM, CZAD, WOD) są **poza zakresem tego skilla** — w raporcie wypisz je wyłącznie informacyjnie ("trafiają do szafy rack / centrali alarmowej"), bez doboru wyposażenia. Wyposażenie strefy niskonapięciowej dopisz do zestawienia zakupowego:

- zakończenie WL wg pytania 7: patch panel krosowy → pozycje "patch panel 24-portowy" (1 na każde rozpoczęte 24 porty WL; to kros do wejść sterownika, nie porty switcha) i "krosówki"; moduły RJ45 (np. EasySwitch) → wpisz jako pozycję z dopiskiem "DIY - zweryfikuj dostępność"; bezpośrednio → dopisz listwy/złączki zaciskowe do wejść sterownika,
- sterowniki świateł/żaluzji i moduły wejść — dobieraj z `sterowniki_katalog.csv` (leży obok tego skilla), filtrując po systemie z wywiadu: sztuki = zaokrąglone w górę (liczba obwodów danej funkcji ÷ `liczba_kanalow`); wejścia pod włączniki (WL) licz z kanałów `input` — u wielu producentów są wbudowane w sterowniki (patrz `uwagi`); jeżeli system ma wiersz `gateway` z dopiskiem "wymagana" — dolicz bramkę; szerokości `szerokosc_moduly` dolicz do bilansu strefy niskonapięciowej; pomijaj wiersze `status_produktu=EOL`, a przy `preorder` ostrzeż o dostępności,
- **dobór zasilaczy** — policz bilans mocy DC zamiast wpisywać zasilacz "na oko":
  - odbiorniki 24 V: sterowniki i bramka (pobór z karty producenta; gdy brak danych załóż 10 W na duży sterownik przekaźnikowy, 2 W na mały moduł magistralowy) oraz ekspandery wejść,
  - suma poboru × 1,4 zapasu → dobierz najmniejszy wystarczający zasilacz z `aparaty_katalog.csv` (porównuj `Pout_W`/`Iout_A` z kolumny `parametry`),
  - taśmy LED (pytanie 8): jeżeli centralnie — osobny zasilacz LED per obwód LED (moc taśmy × 1,25; napięcie wg taśmy — 12 V lub 24 V; nigdy nie wspólny ze sterownikami — zakłócenia i spadki przy przełączaniu), dolicz ich moduły do bilansu i zaznacz kwestię ciepła (przy wielu taśmach zaproponuj osobną obudowę); jeżeli lokalnie — w rozdzielnicy zostają tylko eski B6 dla obwodów zasilaczy,
- listwy zaciskowe przy żaluzjach sterowanych z rozdzielnicy,

**Bilans modułów DIN.** Szerokości aparatów bierz z pliku `aparaty_katalog.csv` (leży obok tego skilla) — filtruj po producencie z wywiadu, a wiersze `generic` traktuj jako fallback, gdy producent nie ma swojego wpisu. Wiersze `generic` podają rezerwę projektową (maksimum z katalogu), nie szerokość konkretnego produktu. Pomijaj wiersze ze `status_produktu=EOL` i `brak`; przy `do_weryfikacji` poinformuj użytkownika, że status produktu trzeba sprawdzić u producenta. Kolumna `parametry` (klucz=wartość;...) niesie cechy istotne przy doborze — ostrzeż użytkownika, gdy licznik ma `pomiar=CT` (wymaga przekładników) lub `MID=0` (nie do rozliczeń), a zasilacz ma `Iout_A` mniejsze niż potrzebne. Dla wallboxa typ RCD (B / B-EV / G/B) zależy od tego, czy ładowarka ma wbudowane wykrywanie 6 mA DC — zapytaj o to w wywiadzie. Gdy pliku brakuje, użyj tabeli poniżej:

| Aparat | Moduły |
|---|---|
| rozłącznik główny 4P | 4 |
| SPD T1+T2 | 4–8 (Hager 8) |
| licznik energii 3F | 4 |
| lampka obecności faz | 1–3 (wg wybranego modelu) |
| różnicówka 4P / 2P | 4 / 2 |
| eska 1P / 3P | 1 / 3 |
| rozłącznik izolacyjny 3P | 3 |
| zasilacz DIN | 2–4 (wg mocy) |
| sterowniki/przekaźniki | wg systemu z wywiadu — podaj założenie |

Do sumy doliczyć **min. 20–30% rezerwy** na przyszłe obwody. Następnie:

- **obudowa już kupiona** → porównaj bilans z jej pojemnością; jeżeli projekt się nie mieści albo rezerwa spada poniżej 20%, powiedz to wprost i zaproponuj, co przenieść (np. strefa niskonapięciowa do osobnej obudowy),
- **obudowy nie ma** → zaproponuj najbliższy typowy rozmiar (rzędy × moduły, np. 4×24) spełniający bilans z rezerwą; wybór podtynkowa/natynkowa zostaw użytkownikowi.

## Faza 3 — zestawienie zakupowe

Na podstawie `obwody.csv` i reguł z Fazy 2 zbuduj zestawienie aparatów i zapisz je do `aparaty.csv` z nagłówkiem: `aparat,grupa,ilosc`. Ten plik jest wejściem do dalszych kroków (np. wyceny).

## Faza 4 — raport

Zapisz `rozdzielnica_projekt.md` zawierający:

1. podsumowanie decyzji z wywiadu,
2. grupy różnicówkowe z przypisanymi obwodami,
3. **bilans modułów**: ile modułów zajmuje projekt, ile zostaje rezerwy oraz werdykt — czy mieści się w posiadanej obudowie / jaką obudowę kupić,
4. **zestawienie zakupowe: tabela "aparat / ile sztuk" per grupa** — to jest główny wynik skilla,
5. listę pozycji specjalnych (wallbox typ B, pompa ciepła — rozłącznik izolacyjny) oraz informacyjną listę obwodów poza rozdzielnicą (szafa rack, centrala alarmowa — bez doboru wyposażenia),
6. disclaimer: projekt poglądowy do weryfikacji przez elektryka z uprawnieniami.
