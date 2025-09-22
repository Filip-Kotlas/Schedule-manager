# Aplikace na vytváření osobního rozvrhu

Aplikace umožňuje vytvářet a upravovat osobní rozvrh.

Pro fungování aplikace, je potřeba mít nainstalovaný python a příslušné balíčky vypsané níže.
Tutoriály k nainstalování pythonu a balíčků by měli být snadno dostupné na google.

Spouští se ze složky se souborem app příkazem "python -m app.rozvrh" (pro nastavení jiného způsobu
spouštění čtěte níže). Po spuštění se otevře okno se seznamem rozvrhů uložených ve složce schedules.
V menu jsou tři možnosti, Rozvrhy, Hodiny a Nastavení.

Při kliknutí na Rozvrhy se
nabídnou další tři možnosti:
    Zobrazit - Zobrazí seznam načtených rozvrhů. Z něho je možné rozvrhy přejmenovat, otevřít nebo
               smazat z tohoto seznamu. V případě, že se jedná o rozvrh uložený ve složce schedules,
               přejmenuje se, respektive smaže se rozvrh i tam.
    Nový - Po dotazu na jméno vytvoří nový rozvrh.
    Otevřít - Po dotazu na soubor načte rozvrh z TXT souboru.
    Uložit - Uloží rozvrh ve formátu TXT do souboru schedules, ze kterého se poté rozvrhy načítají
             při příštím spuštění programu.
    Uložit jako - Po dotazu, kam rozvrh uložit, ho uloží. Je možné uložit rozvrhy ve formátu obrázku
                  (JPEG, PNG, PDF) a ve formátu, ze kterého jdou poté znovu načíst (TXT).

Po kliknutí na Hodiny se otevře nové okno, kde je možné spravovat hodiny v rozvrhu. Tato možnost lze
vybrat pouze pokud je otevřen nějaký rozvrh. V okně je zobrazen seznam hodin v rozvrhu. Označením
hodin a kliknutím na příslušná tlačítka lze hodiny mazat a upravovat. Dále lze hodiny nápodobně
přidávat. Pro přidání a úpravu hodin se otevře další okno, ve kterém může uživatel zadat jméno
hodiny, místo konání, jméno učitele, den konání hodiny, čas začátku a konce hodiny a barvu hodiny
v rozvrhu.

Po kliknutí na Nastavení se otevře okno v kterém může uživatel změnit nastavení vytváření rozvrhů.
Uživatel může určit šířku a výšku rozvrhu v pixelech, orientaci rozvrhu a škálování popisků hodin a
dnů. Dále může nastavit, kdy začíná a končí den a které dny týdne se mají vyobrazovat.

Dependencies:
colorama==0.4.6,
iniconfig==2.0.0,
packaging==24.2,
pillow==11.1.0,
pluggy==1.5.0,
pytest==8.3.4

Testy se pouští pomocí příkazu "pytest" ze stejné složky jako se spouští program.

Pokud chcete aplikaci spouštět ve windows pomocí ikonky zástupce na ploše (nebo jinde), postupujte
následovně. Klikněte pravým tlačítkem myši. Zvolte "Nový" a následně "Zástupce". Do kolonky umístění
souboru vložte příkaz:

C:\Windows\System32\cmd.exe /c cd "umístění_aplikace" & python -m app.rozvrh

kde místo "umístění_aplikace" vložte adresu, kam jste uložili soubory aplikace
(např.: "C:\Users\Filip\Schedule-manager"). Klikněte na "Další". Zadejte jméno zástupce. Klikněte na
dokončit. Nyní lze aplikaci spouštět kliknutím na vzniklého zástupce. Pokud chcete změnit ikonu
zástupce, klikněte na zástupce pravým tlačítkem a zvolte vlastnosti. Ve vyvolaném okénku klikněte na
"Změnit ikonu". Klikněte na "Procházet" a najděte umístění souborů aplikace. Zvolte soubor
"schedule_icon.ico". Klikněte na "OK" a znovu na "OK". Nastavení je kompletní.
