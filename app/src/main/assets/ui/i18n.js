'use strict';
const LANGUAGES={pl:'Polski',de:'Deutsch',en:'English'};
let language=window.Passport?.getLanguage?.()||localStorage.getItem('language')||'pl';
if(!Object.prototype.hasOwnProperty.call(LANGUAGES,language))language='pl';
localStorage.setItem('language',language);if(window.Passport?.setLanguage)window.Passport.setLanguage(language);document.documentElement.lang=language;
const TRANSLATIONS={
 "Polska": {
  "de": "Polen",
  "en": "Poland"
 },
 "Niemcy": {
  "de": "Deutschland",
  "en": "Germany"
 },
 "Ustawienia": {
  "de": "Einstellungen",
  "en": "Settings"
 },
 "⚙ Ustawienia": {
  "de": "⚙ Einstellungen",
  "en": "⚙ Settings"
 },
 "Twój wygląd aplikacji": {
  "de": "Einstellungen",
  "en": "Settings"
 },
 "Wybierz motyw": {
  "de": "Design wählen",
  "en": "Choose a theme"
 },
 "Język aplikacji": {
  "de": "App-Sprache",
  "en": "App language"
 },
 "Gotowe": {
  "de": "Fertig",
  "en": "Done"
 },
 "Szczyty": {
  "de": "Gipfel",
  "en": "Peaks"
 },
 "Przełęcze": {
  "de": "Pässe",
  "en": "Passes"
 },
 "Zamki i pałace": {
  "de": "Burgen und Schlösser",
  "en": "Castles and palaces"
 },
 "Wodospady": {
  "de": "Wasserfälle",
  "en": "Waterfalls"
 },
 "Jaskinie": {
  "de": "Höhlen",
  "en": "Caves"
 },
 "Skały": {
  "de": "Felsen",
  "en": "Rocks"
 },
 "Jeziora i wody": {
  "de": "Seen und Gewässer",
  "en": "Lakes and waters"
 },
 "Przyroda": {
  "de": "Natur",
  "en": "Nature"
 },
 "Punkty widokowe": {
  "de": "Aussichtspunkte",
  "en": "Viewpoints"
 },
 "Zabytki": {
  "de": "Sehenswürdigkeiten",
  "en": "Heritage sites"
 },
 "Latarnie": {
  "de": "Leuchttürme",
  "en": "Lighthouses"
 },
 "Obiekty przemysłowe": {
  "de": "Industriekultur",
  "en": "Industrial sites"
 },
 "Mapa": {
  "de": "Karte",
  "en": "Map"
 },
 "Lista": {
  "de": "Liste",
  "en": "List"
 },
 "Kolekcje": {
  "de": "Sammlungen",
  "en": "Collections"
 },
 "Dziennik": {
  "de": "Tagebuch",
  "en": "Journal"
 },
 "Odznaki": {
  "de": "Abzeichen",
  "en": "Badges"
 },
 "Twój kolejny rozdział": {
  "de": "Dein nächstes Kapitel",
  "en": "Your next chapter"
 },
 "Małe kroki. Wielkie wspomnienia.": {
  "de": "Kleine Schritte. Große Erinnerungen.",
  "en": "Small steps. Great memories."
 },
 "More countries coming soon": {
  "de": "Weitere Länder folgen bald",
  "en": "More countries coming soon"
 },
 "Postęp odwiedzin": {
  "de": "Besuchsfortschritt",
  "en": "Visit progress"
 },
 "Wybór kraju": {
  "de": "Land wählen",
  "en": "Choose country"
 },
 "Nawigacja kraju": {
  "de": "Navigation im Land",
  "en": "Country navigation"
 },
 "Szukaj miejsca lub regionu": {
  "de": "Ort oder Region suchen",
  "en": "Search for a place or region"
 },
 "Szukaj miejsca": {
  "de": "Ort suchen",
  "en": "Search places"
 },
 "Rodzaj miejsca": {
  "de": "Art des Ortes",
  "en": "Place type"
 },
 "Wszystkie rodzaje": {
  "de": "Alle Arten",
  "en": "All types"
 },
 "Nieodwiedzone": {
  "de": "Nicht besucht",
  "en": "Unvisited"
 },
 "✓ Odwiedzone": {
  "de": "✓ Besucht",
  "en": "✓ Visited"
 },
 "Mapa miejsc": {
  "de": "Karte der Orte",
  "en": "Places map"
 },
 "Lista miejsc": {
  "de": "Liste der Orte",
  "en": "Places list"
 },
 "Pokaż bazę HOME": {
  "de": "HOME-Basis anzeigen",
  "en": "Show HOME base"
 },
 "Twoja baza wypadowa": {
  "de": "Dein Ausgangspunkt",
  "en": "Your home base"
 },
 "Nie udało się wczytać części mapy. Punkty i lista pozostają dostępne. Sprawdź połączenie z internetem.": {
  "de": "Teile der Karte konnten nicht geladen werden. Orte und Liste bleiben verfügbar. Prüfe deine Internetverbindung.",
  "en": "Some map tiles could not load. Places and the list remain available. Check your internet connection."
 },
 "Dodaj kolejną wizytę": {
  "de": "Weiteren Besuch hinzufügen",
  "en": "Add another visit"
 },
 "Oznacz jako odwiedzone": {
  "de": "Als besucht markieren",
  "en": "Mark as visited"
 },
 "Propozycja wycieczki": {
  "de": "Ausflugsvorschlag",
  "en": "Suggested visit order"
 },
 "Brak miejsc spełniających filtry. Zmień rodzaj lub wpisaną nazwę.": {
  "de": "Keine passenden Orte. Ändere die Art oder den Suchbegriff.",
  "en": "No matching places. Change the type or search text."
 },
 "Brak miejsc spełniających filtry.": {
  "de": "Keine passenden Orte.",
  "en": "No matching places."
 },
 "Nie udało się wczytać katalogu. Zamknij i otwórz aplikację ponownie.": {
  "de": "Der Katalog konnte nicht geladen werden. Schließe die App und öffne sie erneut.",
  "en": "The catalog could not load. Close and reopen the app."
 },
 "Przygotowanie Twojego paszportu…": {
  "de": "Dein Pass wird vorbereitet…",
  "en": "Preparing your passport…"
 },
 "Edytuj wizytę": {
  "de": "Besuch bearbeiten",
  "en": "Edit visit"
 },
 "Twoja wizyta": {
  "de": "Dein Besuch",
  "en": "Your visit"
 },
 "Data wizyty": {
  "de": "Besuchsdatum",
  "en": "Visit date"
 },
 "Twoja ocena": {
  "de": "Deine Bewertung",
  "en": "Your rating"
 },
 "Bez oceny": {
  "de": "Ohne Bewertung",
  "en": "Not rated"
 },
 "Pogoda": {
  "de": "Wetter",
  "en": "Weather"
 },
 "Słonecznie": {
  "de": "Sonnig",
  "en": "Sunny"
 },
 "Częściowe zachmurzenie": {
  "de": "Teilweise bewölkt",
  "en": "Partly cloudy"
 },
 "Pochmurno": {
  "de": "Bewölkt",
  "en": "Cloudy"
 },
 "Deszcz": {
  "de": "Regen",
  "en": "Rain"
 },
 "Śnieg": {
  "de": "Schnee",
  "en": "Snow"
 },
 "Mgła": {
  "de": "Nebel",
  "en": "Fog"
 },
 "Wiatr": {
  "de": "Wind",
  "en": "Wind"
 },
 "Nie podano": {
  "de": "Nicht angegeben",
  "en": "Not specified"
 },
 "Trasa w AllTrails": {
  "de": "Route in AllTrails",
  "en": "AllTrails route"
 },
 "Dystans (km)": {
  "de": "Distanz (km)",
  "en": "Distance (km)"
 },
 "Czas (minuty)": {
  "de": "Zeit (Minuten)",
  "en": "Time (minutes)"
 },
 "Suma podejść (m)": {
  "de": "Aufstieg gesamt (m)",
  "en": "Total ascent (m)"
 },
 "Notatki": {
  "de": "Notizen",
  "en": "Notes"
 },
 "Co chcesz zapamiętać?": {
  "de": "Was möchtest du festhalten?",
  "en": "What would you like to remember?"
 },
 "Zdjęcia": {
  "de": "Fotos",
  "en": "Photos"
 },
 "(do 10)": {
  "de": "(bis zu 10)",
  "en": "(up to 10)"
 },
 "Dodaj zdjęcie": {
  "de": "Foto hinzufügen",
  "en": "Add photo"
 },
 "Datę i szczegóły możesz później zmienić w Dzienniku.": {
  "de": "Datum und Details kannst du später im Tagebuch ändern.",
  "en": "You can change the date and details later in the Journal."
 },
 "Anuluj": {
  "de": "Abbrechen",
  "en": "Cancel"
 },
 "Zapisz wizytę": {
  "de": "Besuch speichern",
  "en": "Save visit"
 },
 "Wybierz zdjęcie…": {
  "de": "Foto auswählen…",
  "en": "Choose a photo…"
 },
 "Podaj link HTTPS do trasy w AllTrails.": {
  "de": "Gib einen HTTPS-Link zur Route in AllTrails ein.",
  "en": "Enter an HTTPS link to an AllTrails route."
 },
 "Nie udało się zapisać wizyty. Spróbuj ponownie.": {
  "de": "Der Besuch konnte nicht gespeichert werden. Versuche es erneut.",
  "en": "Could not save the visit. Try again."
 },
 "Nie udało się zapisać wizyty. Sprawdź datę, link i wartości formularza.": {
  "de": "Der Besuch konnte nicht gespeichert werden. Prüfe Datum, Link und Eingaben.",
  "en": "Could not save the visit. Check the date, link and form values."
 },
 "Usuń zdjęcie": {
  "de": "Foto entfernen",
  "en": "Remove photo"
 },
 "Zdjęcie dodane.": {
  "de": "Foto hinzugefügt.",
  "en": "Photo added."
 },
 "Nie dodano zdjęcia. Możesz spróbować ponownie.": {
  "de": "Kein Foto hinzugefügt. Du kannst es erneut versuchen.",
  "en": "No photo added. You can try again."
 },
 "Dziennik podróży": {
  "de": "Reisetagebuch",
  "en": "Travel journal"
 },
 "Otwórz trasę w AllTrails ↗": {
  "de": "Route in AllTrails öffnen ↗",
  "en": "Open route in AllTrails ↗"
 },
 "Zdjęcie z wizyty": {
  "de": "Foto vom Besuch",
  "en": "Visit photo"
 },
 "Usuń wizytę": {
  "de": "Besuch löschen",
  "en": "Delete visit"
 },
 "Jeszcze nie masz zapisanych wizyt. Wybierz atrakcję na mapie i oznacz ją jako odwiedzoną.": {
  "de": "Du hast noch keine Besuche gespeichert. Wähle einen Ort auf der Karte und markiere ihn als besucht.",
  "en": "No visits saved yet. Choose a place on the map and mark it as visited."
 },
 "Usunąć tę wizytę?": {
  "de": "Diesen Besuch löschen?",
  "en": "Delete this visit?"
 },
 "Usunięty zostanie ten wpis z notatką, oceną i przypisanymi zdjęciami. Pozostałe wizyty zostaną zachowane.": {
  "de": "Dieser Eintrag wird mit Notiz, Bewertung und zugehörigen Fotos gelöscht. Andere Besuche bleiben erhalten.",
  "en": "This entry, its note, rating and attached photos will be deleted. Other visits will be kept."
 },
 "Nie udało się usunąć wizyty. Spróbuj ponownie.": {
  "de": "Der Besuch konnte nicht gelöscht werden. Versuche es erneut.",
  "en": "Could not delete the visit. Try again."
 },
 "Postęp kolekcji": {
  "de": "Sammlungsfortschritt",
  "en": "Collection progress"
 },
 "‹ Wszystkie kolekcje": {
  "de": "‹ Alle Sammlungen",
  "en": "‹ All collections"
 },
 "Odwiedzone miejsca na górze": {
  "de": "Besuchte Orte zuerst",
  "en": "Visited places first"
 },
 "Szukaj w kolekcji": {
  "de": "In der Sammlung suchen",
  "en": "Search collection"
 },
 "Twój paszport odkryć": {
  "de": "Dein Entdeckerpass",
  "en": "Your passport to discovery"
 },
 "Tematyczne": {
  "de": "Thematisch",
  "en": "Thematic"
 },
 "Pasma i regiony": {
  "de": "Gebirge und Regionen",
  "en": "Ranges and regions"
 },
 "Kolejność odwiedzin": {
  "de": "Besuchsreihenfolge",
  "en": "Visit order"
 },
 "Zapisz miejsca w takiej kolejności, w jakiej chcesz je odwiedzić.": {
  "de": "Speichere Orte in der Reihenfolge, in der du sie besuchen möchtest.",
  "en": "Save places in the order you want to visit them."
 },
 "Postęp obejmuje miejsca dostępne w obecnej bazie.": {
  "de": "Der Fortschritt umfasst Orte im aktuellen Katalog.",
  "en": "Progress covers places in the current catalog."
 },
 "+ Ułóż własną kolejność": {
  "de": "+ Eigene Reihenfolge erstellen",
  "en": "+ Create your own order"
 },
 "Twoja lista": {
  "de": "Deine Liste",
  "en": "Your list"
 },
 "Propozycja": {
  "de": "Vorschlag",
  "en": "Suggestion"
 },
 "Brak pasujących miejsc.": {
  "de": "Keine passenden Orte.",
  "en": "No matching places."
 },
 "Zamknij szczegóły": {
  "de": "Details schließen",
  "en": "Close details"
 },
 "‹ Wróć": {
  "de": "‹ Zurück",
  "en": "‹ Back"
 },
 "Pokaż na mapie": {
  "de": "Auf der Karte anzeigen",
  "en": "Show on map"
 },
 "Kolejność odwiedzin możesz dopasować do swojego wyjazdu.": {
  "de": "Du kannst die Besuchsreihenfolge an deine Reise anpassen.",
  "en": "You can adjust the visit order to suit your trip."
 },
 "Nie ma jeszcze zapisanej propozycji dla tego miejsca.": {
  "de": "Für diesen Ort gibt es noch keinen gespeicherten Vorschlag.",
  "en": "There is no saved suggestion for this place yet."
 },
 "Ułóż własną kolejność": {
  "de": "Eigene Reihenfolge erstellen",
  "en": "Create your own order"
 },
 "Kolejność odwiedzin · bez wyznaczania przebiegu trasy": {
  "de": "Besuchsreihenfolge · ohne Routenberechnung",
  "en": "Visit order · no route calculation"
 },
 "Edytuj kolejność": {
  "de": "Reihenfolge bearbeiten",
  "en": "Edit order"
 },
 "Zapisz własną wersję": {
  "de": "Eigene Version speichern",
  "en": "Save your own version"
 },
 "Usuń listę": {
  "de": "Liste löschen",
  "en": "Delete list"
 },
 "Twoja kolejność odwiedzin": {
  "de": "Deine Besuchsreihenfolge",
  "en": "Your visit order"
 },
 "Nazwa listy": {
  "de": "Listenname",
  "en": "List name"
 },
 "Np. Weekend w górach": {
  "de": "Z. B. Wochenende in den Bergen",
  "en": "E.g. Weekend in the mountains"
 },
 "Dodaj miejsce": {
  "de": "Ort hinzufügen",
  "en": "Add place"
 },
 "Wpisz nazwę miejsca": {
  "de": "Ortsnamen eingeben",
  "en": "Enter place name"
 },
 "Zapisz kolejność": {
  "de": "Reihenfolge speichern",
  "en": "Save order"
 },
 "Wpisz nazwę i dodaj co najmniej dwa różne miejsca.": {
  "de": "Gib einen Namen ein und füge mindestens zwei verschiedene Orte hinzu.",
  "en": "Enter a name and add at least two different places."
 },
 "Usuń": {
  "de": "Entfernen",
  "en": "Remove"
 },
 "Brak nowych pasujących miejsc.": {
  "de": "Keine weiteren passenden Orte.",
  "en": "No new matching places."
 },
 "Nie udało się zapisać listy. Spróbuj ponownie.": {
  "de": "Die Liste konnte nicht gespeichert werden. Versuche es erneut.",
  "en": "Could not save the list. Try again."
 },
 "Usunąć listę?": {
  "de": "Liste löschen?",
  "en": "Delete list?"
 },
 "Wizyty i ich postęp pozostaną zapisane.": {
  "de": "Besuche und ihr Fortschritt bleiben gespeichert.",
  "en": "Visits and their progress will be kept."
 },
 "Błąd zapisu — spróbuj ponownie": {
  "de": "Speicherfehler — versuche es erneut",
  "en": "Save failed — try again"
 },
 "Lista może zawierać maksymalnie 100 miejsc.": {
  "de": "Eine Liste kann höchstens 100 Orte enthalten.",
  "en": "A list can contain up to 100 places."
 },
 "Kopia danych — eksport / import": {
  "de": "Datensicherung — Export / Import",
  "en": "Backup — export / import"
 },
 "Kopia Twoich wspomnień": {
  "de": "Sichere deine Erinnerungen",
  "en": "Back up your memories"
 },
 "Jeden plik ZIP: wizyty, zdjęcia, oceny, własne listy i ustawienia.": {
  "de": "Eine ZIP-Datei: Besuche, Fotos, Bewertungen, eigene Listen und Einstellungen.",
  "en": "One ZIP file: visits, photos, ratings, custom lists and settings."
 },
 "Zapisz kopię": {
  "de": "Sicherung speichern",
  "en": "Save backup"
 },
 "Wczytaj kopię": {
  "de": "Sicherung laden",
  "en": "Load backup"
 },
 "Wybierasz miejsce zapisu. Aplikacja nie wysyła kopii na serwer. Plik zawiera Twoje notatki i zdjęcia — przechowuj go w wybranym przez siebie miejscu.": {
  "de": "Du wählst den Speicherort. Die App sendet keine Sicherung an einen Server. Die Datei enthält deine Notizen und Fotos — bewahre sie an einem Ort deiner Wahl auf.",
  "en": "You choose where to save it. The app does not upload backups to a server. The file contains your notes and photos — store it in a location of your choice."
 },
 "Zamknij": {
  "de": "Schließen",
  "en": "Close"
 },
 "Zapis i odczyt pliku są dostępne w aplikacji Android.": {
  "de": "Dateien können in der Android-App gespeichert und geladen werden.",
  "en": "Saving and loading files is available in the Android app."
 },
 "Wybierz plik w oknie telefonu…": {
  "de": "Wähle eine Datei im Dialog deines Telefons…",
  "en": "Choose a file in the phone dialog…"
 },
 "Podsumowanie kopii": {
  "de": "Übersicht der Sicherung",
  "en": "Backup summary"
 },
 "Połącz dane": {
  "de": "Daten zusammenführen",
  "en": "Merge data"
 },
 "ekran główny": {
  "de": "Startseite",
  "en": "home screen"
 },
 "Nie można otworzyć wyboru pliku.": {
  "de": "Die Dateiauswahl konnte nicht geöffnet werden.",
  "en": "Could not open the file picker."
 },
 "Anulowano wybór pliku.": {
  "de": "Dateiauswahl abgebrochen.",
  "en": "File selection cancelled."
 },
 "Kopia danych została zapisana.": {
  "de": "Die Sicherung wurde gespeichert.",
  "en": "Backup saved."
 },
 "Nie udało się zapisać pełnej kopii. Sprawdź wolne miejsce i spróbuj ponownie.": {
  "de": "Die Sicherung konnte nicht vollständig gespeichert werden. Prüfe den freien Speicher und versuche es erneut.",
  "en": "Could not save the complete backup. Check free storage and try again."
 },
 "Plik jest uszkodzony, niezgodny lub przekracza limit kopii. Twoje dane nie zostały zmienione.": {
  "de": "Die Datei ist beschädigt, inkompatibel oder zu groß. Deine Daten wurden nicht verändert.",
  "en": "The file is damaged, incompatible or exceeds the backup limit. Your data has not been changed."
 },
 "Wybierz ponownie plik kopii.": {
  "de": "Wähle die Sicherungsdatei erneut aus.",
  "en": "Select the backup file again."
 },
 "Dane zostały połączone.": {
  "de": "Die Daten wurden zusammengeführt.",
  "en": "Data merged."
 },
 "Nie udało się połączyć danych. Poprzednie dane zostały zachowane.": {
  "de": "Die Daten konnten nicht zusammengeführt werden. Bisherige Daten wurden beibehalten.",
  "en": "Could not merge data. Existing data has been kept."
 },
 "Podgląd": {
  "de": "Vorschau",
  "en": "Preview"
 },
 "Przygotowanie odznak…": {
  "de": "Abzeichen werden vorbereitet…",
  "en": "Preparing badges…"
 },
 "Każdy krok się liczy": {
  "de": "Jeder Schritt zählt",
  "en": "Every step counts"
 },
 "Twoje odznaki": {
  "de": "Deine Abzeichen",
  "en": "Your badges"
 },
 "Podgląd progów do uzgodnienia. Trwałe odblokowania nie są jeszcze przyznawane.": {
  "de": "Vorschau der Schwellenwerte zur Abstimmung. Dauerhafte Freischaltungen werden noch nicht vergeben.",
  "en": "Threshold preview for agreement. Permanent unlocks are not awarded yet."
 },
 "Wymaga uzupełnienia oznaczeń w bazie": {
  "de": "Erfordert ergänzte Kennzeichnungen im Katalog",
  "en": "Requires catalog labels to be completed"
 },
 " · podgląd postępu": {
  "de": " · Fortschrittsvorschau",
  "en": " · progress preview"
 },
 "Próg:": {
  "de": "Schwellenwert:",
  "en": "Threshold:"
 },
 "Robocza propozycja — bez zapisu daty zdobycia.": {
  "de": "Entwurf — ohne Speicherung des Erwerbsdatums.",
  "en": "Draft — acquisition date is not saved."
 },
 "Ta rodzina wymaga zweryfikowanych oznaczeń w katalogu.": {
  "de": "Diese Familie erfordert geprüfte Kennzeichnungen im Katalog.",
  "en": "This family requires verified catalog labels."
 },
 "Odkrywca": {
  "de": "Entdecker",
  "en": "Explorer"
 },
 "Dystans": {
  "de": "Distanz",
  "en": "Distance"
 },
 "Suma podejść": {
  "de": "Aufstieg gesamt",
  "en": "Total ascent"
 },
 "Czas w terenie": {
  "de": "Zeit unterwegs",
  "en": "Time outdoors"
 },
 "Miejsca obowiązkowe": {
  "de": "Sehenswerte Orte",
  "en": "Must-see places"
 },
 "Odkrywca regionów": {
  "de": "Regionen entdecken",
  "en": "Regional explorer"
 },
 "Kolekcjoner": {
  "de": "Sammler",
  "en": "Collector"
 },
 "Paszport kraju": {
  "de": "Länderpass",
  "en": "Country passport"
 },
 "miejsc": {
  "de": "Orte",
  "en": "places"
 },
 "regionów": {
  "de": "Regionen",
  "en": "regions"
 },
 "kolekcji": {
  "de": "Sammlungen",
  "en": "collections"
 },
 "Bronze I": {
  "de": "Bronze I",
  "en": "Bronze I"
 },
 "Bronze II": {
  "de": "Bronze II",
  "en": "Bronze II"
 },
 "Silver I": {
  "de": "Silber I",
  "en": "Silver I"
 },
 "Silver II": {
  "de": "Silber II",
  "en": "Silver II"
 },
 "Gold I": {
  "de": "Gold I",
  "en": "Gold I"
 },
 "Gold II": {
  "de": "Gold II",
  "en": "Gold II"
 },
 "Diamond I": {
  "de": "Diamant I",
  "en": "Diamond I"
 },
 "Diamond II": {
  "de": "Diamant II",
  "en": "Diamond II"
 },
 "Źródła i informacje prawne": {
  "de": "Quellen und rechtliche Hinweise",
  "en": "Sources and legal information"
 },
 "Źródła mapy": {
  "de": "Kartenquellen",
  "en": "Map sources"
 },
 "Prywatność mapy": {
  "de": "Datenschutz der Karte",
  "en": "Map privacy"
 },
 "Wróć do ustawień": {
  "de": "Zurück zu den Einstellungen",
  "en": "Back to settings"
 },
 "Granice: Natural Earth — domena publiczna": {
  "de": "Grenzen: Natural Earth — gemeinfrei",
  "en": "Boundaries: Natural Earth — public domain"
 },
 "Mapa: © OpenStreetMap contributors. Podkład mapowy wymaga internetu; katalog miejsc jest zapisany w aplikacji.": {
  "de": "Karte: © OpenStreetMap contributors. Die Hintergrundkarte benötigt Internet; der Ortskatalog ist in der App gespeichert.",
  "en": "Map: © OpenStreetMap contributors. Map tiles require internet; the places catalog is stored in the app."
 },
 "Lokalizacje: OpenStreetMap / Photon, GeoNames oraz źródła katalogu. Punkty obszarów mogą wskazywać ich środek, a nie wejście. Granice krajów są uproszczone i służą prezentacji mapy.": {
  "de": "Standorte: OpenStreetMap / Photon, GeoNames und Katalogquellen. Gebietspunkte können die Mitte statt eines Eingangs markieren. Ländergrenzen sind für die Kartendarstellung vereinfacht.",
  "en": "Locations: OpenStreetMap / Photon, GeoNames and catalog sources. Area points may mark the center rather than an entrance. Country boundaries are simplified for map display."
 },
 "Wizyty, notatki i kopie wybranych zdjęć są zapisywane lokalnie na urządzeniu. Aplikacja nie wysyła ich na serwer. Pobieranie kafelków mapy ujawnia dostawcy adres IP i oglądany obszar. Otwarcie linku AllTrails lub źródła odbywa się w zewnętrznej przeglądarce. Usunięcie danych aplikacji usuwa lokalny dziennik; kopię możesz zapisać w ustawieniach aplikacji.": {
  "de": "Besuche, Notizen und Kopien ausgewählter Fotos werden lokal auf dem Gerät gespeichert. Die App sendet sie nicht an einen Server. Beim Laden von Kartenkacheln erhält der Anbieter die IP-Adresse und den betrachteten Bereich. AllTrails- und Quellenlinks öffnen sich in einem externen Browser. Das Löschen der App-Daten entfernt das lokale Tagebuch; eine Sicherung kannst du in den Einstellungen speichern.",
  "en": "Visits, notes and copies of selected photos are stored locally on the device. The app does not send them to a server. Loading map tiles reveals your IP address and viewed area to the provider. AllTrails and source links open in an external browser. Clearing app data removes the local journal; you can save a backup in settings."
 },
 "Materiały do propozycji odwiedzin:": {
  "de": "Quellen für Besuchsvorschläge:",
  "en": "Sources for suggested visits:"
 },
 "{done} / {total} miejsc na mapie odwiedzonych": {
  "de": "{done} / {total} Kartenorte besucht",
  "en": "{done} / {total} map places visited"
 },
 "{count} z {total} miejsc na mapie": {
  "de": "{count} von {total} Orten auf der Karte",
  "en": "{count} of {total} places on the map"
 },
 "{done} / {total} odwiedzonych": {
  "de": "{done} / {total} besucht",
  "en": "{done} / {total} visited"
 },
 "Ocena {n} z 5": {
  "de": "Bewertung {n} von 5",
  "en": "Rating {n} of 5"
 },
 "Zdjęcie z wizyty {n}": {
  "de": "Besuchsfoto {n}",
  "en": "Visit photo {n}"
 },
 "Usuń wizytę: {name}, {date}": {
  "de": "Besuch löschen: {name}, {date}",
  "en": "Delete visit: {name}, {date}"
 },
 "Przesuń {name} w górę": {
  "de": "{name} nach oben verschieben",
  "en": "Move {name} up"
 },
 "Przesuń {name} w dół": {
  "de": "{name} nach unten verschieben",
  "en": "Move {name} down"
 },
 "Usuń {name} z listy": {
  "de": "{name} aus der Liste entfernen",
  "en": "Remove {name} from list"
 },
 "Twój obecny wynik: {value} {unit}.": {
  "de": "Dein aktueller Stand: {value} {unit}.",
  "en": "Your current result: {value} {unit}."
 },
 "Nowe wizyty: {n}": {
  "de": "Neue Besuche: {n}",
  "en": "New visits: {n}"
 },
 "Nowe listy: {n}": {
  "de": "Neue Listen: {n}",
  "en": "New lists: {n}"
 },
 "Zdjęcia w kopii: {n}": {
  "de": "Fotos in der Sicherung: {n}",
  "en": "Photos in backup: {n}"
 },
 "Pominięte istniejące wpisy: {visits}; listy: {plans}. Obecne wpisy zachowają swoje dane, również jeśli różnią się od kopii.": {
  "de": "Übersprungene vorhandene Einträge: {visits}; Listen: {plans}. Vorhandene Einträge behalten ihre Daten, auch wenn sie von der Sicherung abweichen.",
  "en": "Existing entries skipped: {visits}; lists: {plans}. Existing entries keep their data, even if it differs from the backup."
 },
 "Przywrócimy ustawienia z kopii: {theme}, kraj: {country}, język: {language}.": {
  "de": "Einstellungen aus der Sicherung: {theme}, Land: {country}, Sprache: {language}.",
  "en": "Settings to restore: {theme}, country: {country}, language: {language}."
 },
 "Zachowaj obecny język": {
  "de": "Aktuelle Sprache beibehalten",
  "en": "Keep current language"
 }
};
Object.assign(TRANSLATIONS,{"Brocken i Brockengarten": {"de": "Brocken und Brockengarten", "en": "Brocken and Brockengarten"}, "Malinów, Jaskinia Malinowska i dwa szczyty pasma Skrzycznego. Dopasuj kolejność do swojego wyjazdu.": {"de": "Malinów, Jaskinia Malinowska und zwei Gipfel im Skrzyczne-Gebiet. Passe die Reihenfolge an deine Reise an.", "en": "Malinów, Jaskinia Malinowska and two peaks in the Skrzyczne range. Adjust the order to your trip."}, "Szczyt i ogród na Brocken. Wizyty w ogrodzie odbywają się według zasad i terminów parku.": {"de": "Gipfel und Garten auf dem Brocken. Für Gartenbesuche gelten die Regeln und Termine des Parks.", "en": "The summit and garden on the Brocken. Garden visits follow the park’s rules and schedule."}});
Object.assign(TRANSLATIONS,{'Powiększ':{de:'Vergrößern',en:'Zoom in'},'Pomniejsz':{de:'Verkleinern',en:'Zoom out'}});
Object.assign(TRANSLATIONS,{"Nie udało się zapisać odznak. Otwórz tę zakładkę ponownie, aby spróbować jeszcze raz.": {"de": "Abzeichen konnten nicht gespeichert werden. Öffne diesen Tab erneut, um es noch einmal zu versuchen.", "en": "Could not save badges. Open this tab again to retry."}, "Zdobyte odznaki i ich daty pozostają zapisane. Bieżący postęp wynika z Twoich wizyt.": {"de": "Erworbene Abzeichen und ihre Daten bleiben gespeichert. Der aktuelle Fortschritt ergibt sich aus deinen Besuchen.", "en": "Earned badges and their dates remain saved. Current progress is based on your visits."}, "Zdobyto: {date}": {"de": "Erworben: {date}", "en": "Earned: {date}"}, "Jeszcze niezdobyta": {"de": "Noch nicht erworben", "en": "Not earned yet"}, "Następny próg:": {"de": "Nächster Schwellenwert:", "en": "Next threshold:"}, "Wszystkie poziomy zdobyte": {"de": "Alle Stufen erworben", "en": "All tiers earned"}, "Odznaki w kopii: {n}": {"de": "Abzeichen in der Sicherung: {n}", "en": "Badges in backup: {n}"}, "Wyróżnione Must See": {"de": "Must-See-Auswahl", "en": "Must See selection"}});
Object.assign(TRANSLATIONS,{"Szczyty — {region}":{"de":"Gipfel — {region}","en":"Peaks — {region}"}});
function t(key,params={}){const message=language==='pl'?key:(TRANSLATIONS[key]?.[language]??key);return message.replace(/\{(\w+)\}/g,(_,name)=>String(params[name]??'{'+name+'}'));}
function translateStatic(){document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n);});}
function languageChoices(){const box=document.querySelector('#languageChoices');box.innerHTML=Object.entries(LANGUAGES).map(([id,name])=>`<button data-language-choice="${id}" aria-pressed="${language===id}">${name}</button>`).join('');box.querySelectorAll('button').forEach(button=>button.onclick=()=>{const selected=button.dataset.languageChoice;if(window.Passport?.setLanguage)window.Passport.setLanguage(selected);localStorage.setItem('language',selected);location.reload();});}
document.addEventListener('DOMContentLoaded',translateStatic,{once:true});

Object.assign(TRANSLATIONS,{"Trasa / AllTrails": {"de": "Route / AllTrails", "en": "Route / AllTrails"}, "Dzień odwiedzin": {"de": "Besuchstag", "en": "Visit date"}, "Ocena minimalna": {"de": "Mindestbewertung", "en": "Minimum rating"}, "Wszystkie oceny": {"de": "Alle Bewertungen", "en": "All ratings"}, "Sortowanie": {"de": "Sortierung", "en": "Sort order"}, "Najnowsze": {"de": "Neueste zuerst", "en": "Newest first"}, "Najstarsze": {"de": "Älteste zuerst", "en": "Oldest first"}, "Najwyżej ocenione": {"de": "Beste Bewertung", "en": "Highest rated"}, "Wyczyść filtry": {"de": "Filter zurücksetzen", "en": "Clear filters"}, "Brak wizyt spełniających filtry.": {"de": "Keine passenden Besuche.", "en": "No visits match these filters."}, "Zdobyte progi": {"de": "Erreichte Stufen", "en": "Earned tiers"}, "Próg {n}": {"de": "Stufe {n}", "en": "Tier {n}"}, "Bieżący postęp": {"de": "Aktueller Fortschritt", "en": "Current progress"}, "szczyt": {"de": "Gipfel", "en": "peak"}, "szczyty": {"de": "Gipfel", "en": "peaks"}, "szczytów": {"de": "Gipfel", "en": "peaks"}, "zamek": {"de": "Burg", "en": "castle"}, "zamki": {"de": "Burgen", "en": "castles"}, "zamków": {"de": "Burgen", "en": "castles"}, "jaskinia": {"de": "Höhle", "en": "cave"}, "jaskinie": {"de": "Höhlen", "en": "caves"}, "jaskiń": {"de": "Höhlen", "en": "caves"}, "wodospad": {"de": "Wasserfall", "en": "waterfall"}, "wodospady": {"de": "Wasserfälle", "en": "waterfalls"}, "wodospadów": {"de": "Wasserfälle", "en": "waterfalls"}, "Usunięty zostanie ten wpis z notatką i oceną. Pozostałe wizyty zostaną zachowane.": {"de": "Dieser Eintrag mit Notiz und Bewertung wird gelöscht. Andere Besuche bleiben erhalten.", "en": "This entry, its note and rating will be deleted. Other visits will be kept."}, "Jeden plik ZIP: wizyty, oceny, odznaki, własne listy i ustawienia.": {"de": "Eine ZIP-Datei: Besuche, Bewertungen, Abzeichen, eigene Listen und Einstellungen.", "en": "One ZIP file: visits, ratings, badges, custom lists and settings."}, "Wybierasz miejsce zapisu. Aplikacja nie wysyła kopii na serwer. Plik zawiera Twoje dane — przechowuj go w wybranym przez siebie miejscu.": {"de": "Du wählst den Speicherort. Die App lädt die Sicherung nicht auf einen Server hoch. Die Datei enthält deine persönlichen Daten.", "en": "Choose where to save it. The app does not upload the backup to a server. The file contains your personal data."}, "Trasa: maksymalnie 4000 znaków.": {"de": "Route: maximal 4000 Zeichen.", "en": "Route: maximum 4000 characters."}, "Odwiedzaj różne szczyty w wybranym kraju. Każdy szczyt liczy się raz.": {"de": "Besuche verschiedene Gipfel im ausgewählten Land. Jeder Gipfel zählt einmal.", "en": "Visit distinct peaks in the selected country. Each peak counts once."}, "Odwiedzaj różne miejsca w wybranym kraju. Powtórne wizyty nie zwiększają liczby miejsc.": {"de": "Besuche verschiedene Orte im ausgewählten Land. Wiederholte Besuche erhöhen die Anzahl nicht.", "en": "Visit distinct places in the selected country. Repeat visits do not increase the place count."}, "Zbieraj kilometry zapisane w wizytach w wybranym kraju. Sumujemy dystans wszystkich wizyt.": {"de": "Sammle Kilometer bei Besuchen im ausgewählten Land. Die Entfernungen aller Besuche werden addiert.", "en": "Accumulate distance recorded in visits in the selected country. Distances from all visits are added."}, "Zbieraj metry podejść zapisane w wizytach w wybranym kraju. Powtórne wejścia też się liczą.": {"de": "Sammle bei Besuchen im ausgewählten Land aufgezeichnete Höhenmeter. Wiederholte Aufstiege zählen ebenfalls.", "en": "Accumulate ascent recorded in visits in the selected country. Repeat ascents also count."}, "Zbieraj czas zapisany w wizytach w wybranym kraju. Minuty przeliczamy na godziny.": {"de": "Sammle bei Besuchen im ausgewählten Land aufgezeichnete Zeit. Minuten werden in Stunden umgerechnet.", "en": "Accumulate time recorded in visits in the selected country. Minutes are converted to hours."}, "Odwiedzaj różne zamki i pałace w wybranym kraju. Każdy obiekt liczy się raz.": {"de": "Besuche verschiedene Burgen und Schlösser im ausgewählten Land. Jeder Ort zählt einmal.", "en": "Visit distinct castles and palaces in the selected country. Each place counts once."}, "Odwiedzaj różne jaskinie w wybranym kraju. Każda jaskinia liczy się raz.": {"de": "Besuche verschiedene Höhlen im ausgewählten Land. Jede Höhle zählt einmal.", "en": "Visit distinct caves in the selected country. Each cave counts once."}, "Odwiedzaj różne wodospady w wybranym kraju. Każdy wodospad liczy się raz.": {"de": "Besuche verschiedene Wasserfälle im ausgewählten Land. Jeder Wasserfall zählt einmal.", "en": "Visit distinct waterfalls in the selected country. Each waterfall counts once."}, "Odwiedzaj miejsca oznaczone Must See na mapie wybranego kraju. Każde miejsce liczy się raz.": {"de": "Besuche als Must See markierte Orte auf der Karte des ausgewählten Landes. Jeder Ort zählt einmal.", "en": "Visit places marked Must See on the selected country’s map. Each place counts once."}, "Odwiedź przynajmniej jedno miejsce w różnych województwach Polski lub landach Niemiec. Każdy region liczy się raz.": {"de": "Besuche mindestens einen Ort in verschiedenen polnischen Woiwodschaften oder deutschen Bundesländern. Jede Region zählt einmal.", "en": "Visit at least one place in distinct Polish provinces or German states. Each region counts once."}, "Odwiedź wszystkie miejsca kolekcji, aby ją ukończyć. Liczymy ukończone kolekcje wybranego kraju; własne listy nie są kolekcjami.": {"de": "Besuche alle Orte einer Sammlung, um sie abzuschließen. Abgeschlossene Sammlungen des ausgewählten Landes zählen; eigene Listen zählen nicht.", "en": "Visit every place in a collection to complete it. Completed collections in the selected country count; custom lists do not."}, "Odwiedzaj miejsca dostępne na mapie wybranego kraju. Wynik to procent odwiedzonego katalogu; może się zmienić po rozbudowie bazy.": {"de": "Besuche Orte auf der Karte des ausgewählten Landes. Der Wert ist der besuchte Kataloganteil und kann sich bei einer Erweiterung ändern.", "en": "Visit places on the selected country’s map. Progress is the percentage of the catalog visited and may change when the catalog grows."}});

Object.assign(TRANSLATIONS,{"Wizyty i notatki są zapisywane lokalnie na urządzeniu. Aplikacja nie wysyła ich na serwer. Pobieranie kafelków mapy ujawnia dostawcy adres IP i oglądany obszar. Linki do źródeł otwierają się w zewnętrznej przeglądarce. Usunięcie danych aplikacji usuwa lokalny dziennik; kopię możesz zapisać w ustawieniach aplikacji.": {"de": "Besuche und Notizen werden lokal auf dem Gerät gespeichert und nicht auf einen Server hochgeladen. Beim Laden von Kartenkacheln erhält der Anbieter deine IP-Adresse und den angezeigten Bereich. Quellenlinks öffnen sich im externen Browser. Das Löschen der App-Daten entfernt das lokale Tagebuch; Sicherungen kannst du in den Einstellungen erstellen.", "en": "Visits and notes are stored locally on your device and are not uploaded to a server. Loading map tiles reveals your IP address and viewed area to the provider. Source links open in an external browser. Clearing app data removes the local journal; you can create a backup in settings."}});

Object.assign(TRANSLATIONS,{"Próg {n} - cel:": {"de": "Stufe {n} - Ziel:", "en": "Tier {n} - target:"}, "Następny:": {"de": "Nächste Stufe:", "en": "Next:"}, "Wszystkie progi": {"de": "Alle Stufen", "en": "All tiers"}});

Object.assign(TRANSLATIONS,{
  "Ocena {n} z 10": {
    "de": "Bewertung {n} von 10",
    "en": "Rating {n} out of 10"
  },
  "Ocena {n} z {max}": {
    "de": "Bewertung {n} von {max}",
    "en": "Rating {n} out of {max}"
  },
  "Wycieczki": {
    "de": "Ausflüge",
    "en": "Trips"
  },
  "Dodaj własną Wycieczkę": {
    "de": "Eigenen Ausflug hinzufügen",
    "en": "Add your own trip"
  },
  "+ Dodaj własną Wycieczkę": {
    "de": "+ Eigenen Ausflug hinzufügen",
    "en": "+ Add your own trip"
  },
  "Wycieczka · kolejność odwiedzin": {
    "de": "Ausflug · Besuchsreihenfolge",
    "en": "Trip · visiting order"
  },
  "Ten wpis pochodzi sprzed zmian formularza. Edytuj go, sprawdź ocenę w nowej skali 1–10 i zapisz ponownie. Dane zostały zachowane.": {
    "de": "Dieser Eintrag stammt aus dem alten Formular. Bearbeite ihn, prüfe die Bewertung auf der neuen Skala von 1–10 und speichere ihn erneut. Deine Daten wurden beibehalten.",
    "en": "This entry uses the old form. Edit it, review the rating on the new 1–10 scale and save it again. Your data has been preserved."
  }
});

Object.assign(TRANSLATIONS,{'Bieżąca wersja':{de:'Aktuelle Version',en:'Current version'}});
