"""Constants for the DWD Enthalpie integration."""
from __future__ import annotations

DOMAIN = "dwd_enthalpie"

# Source URL — DWD landwirtschaftlicher Warnindex "Enthalpie" (Hitzestress)
SOURCE_URL = (
    "https://www.wettergefahren.de/warnungen/indizes_landwirtschaft/enthalpie.html"
)

# How often to refresh. The DWD updates this page roughly once per day.
# Hourly is polite and gives reasonable freshness if the DWD updates twice.
UPDATE_INTERVAL_MINUTES = 60

# Config entry data key
CONF_STATIONS = "stations"

# Heat-stress classification thresholds (kJ/kg, daily maximum enthalpy)
# Source: DWD legend on the source page.
CLASS_NONE = "kein Hitzestress"
CLASS_MILD = "milder Hitzestress"
CLASS_MODERATE = "mäßiger Hitzestress"
CLASS_STRONG = "starker Hitzestress"
CLASS_EXTREME = "extremer Hitzestress"
CLASS_UNKNOWN = "unbekannt"


def classify(value: float | int | None) -> str:
    """Map an enthalpy value (kJ/kg) to its DWD heat-stress class."""
    if value is None:
        return CLASS_UNKNOWN
    if value < 50:
        return CLASS_NONE
    if value < 58:
        return CLASS_MILD
    if value < 67:
        return CLASS_MODERATE
    if value < 72:
        return CLASS_STRONG
    return CLASS_EXTREME


# German federal states (Bundesländer) as they appear in the DWD page headings.
# Used for the first step of the config flow.
BUNDESLAENDER: tuple[str, ...] = (
    "Baden-Württemberg",
    "Bayern",
    "Berlin",
    "Brandenburg",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Saarland",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thüringen",
)

# Static station list per Bundesland — extracted from the DWD page.
# If the DWD adds or removes a station, update this list.
# Order matches the DWD page (north → south within each state).
STATIONS_BY_STATE: dict[str, tuple[str, ...]] = {
    "Baden-Württemberg": (
        "Freudenberg-Boxtal/Main", "Buchen (Kreis Neckar-Odenwald)", "Mannheim",
        "Bad Mergentheim", "Niederstetten", "Ingelfingen-Stachenhausen", "Waibstadt",
        "Waghäusel-Kirrlach", "Öhringen", "Kirchberg-Herboldshausen/Jagst",
        "Eppingen-Elsenz", "Obersulm-Willsbach", "Großerlach-Mannenweiler",
        "Ellwangen-Rindelbach", "Rheinstetten", "Mühlacker", "Sachsenheim",
        "Pforzheim-Ispringen", "Kaisersbach-Cronhütte", "Stuttgart (Schnarrenberg)",
        "Schwäbisch Gmünd-Weiler", "Renningen", "Baden-Baden-Geroldsau",
        "Stuttgart (Flughafen)", "Rheinau-Memprechtshofen", "Notzingen", "Stötten",
        "Neubulach-Oberhaugstett", "Hermaringen-Allewind",
        "Seebach (Nationalpark Schwarzwald)", "Metzingen", "Freudenstadt",
        "Ulm-Mähringen", "Ohlsbach", "Münsingen-Apfelstetten", "Hechingen", "Lahr",
        "Wolfach", "Balingen-Bronnhaupten", "Laupheim", "Elzach-Fisnacht", "Rottweil",
        "Meßstetten-Appental", "Altheim (Kreis Biberach)", "Emmendingen-Mundingen",
        "Klippeneck", "Sigmaringen-Laiz", "Villingen-Schwenningen", "Freiburg",
        "Buchenbach", "Pfullendorf", "Lenzkirch-Ruhbühl", "Müllheim",
        "Weingarten (Kreis Ravensburg)", "Leutkirch-Herlazhofen", "Singen",
        "Dachsberg-Wolpadingen", "Konstanz", "Friedrichshafen-Unterraderach",
        "Wutöschingen-Ofteringen", "Rheinfelden",
    ),
    "Bayern": (
        "Ostheim vor der Rhön", "Teuschnitz", "Sandberg", "Hof", "Lautertal-Oberlauter",
        "Bad Königshofen", "Kronach", "Bad Kissingen", "Schönwald/Ofr.-Brunn",
        "Staffelstein, Bad-Stublang", "Kahl/Main", "Schonungen-Mainberg",
        "Wunsiedel-Schönbrunn", "Lohr-Halsbach/Main", "Neuhütten/Spessart",
        "Fichtelberg-Hüttstadl/Oberfranken", "Arnstein-Müdesheim",
        "Heinersreuth-Vollhof", "Bamberg", "Tirschenreuth-Lodermühl", "Ebrach",
        "Neustadt-Filchendorf am Kulm", "Würzburg", "Röllbach", "Kitzingen", "Weiden",
        "Gräfenberg-Kasberg", "Möhrendorf-Kleinseebach", "Gollhofen",
        "Nürnberg (Flughafen)", "Markt Erlbach-Hagenhofen", "Pommelsbrunn-Mittelburg",
        "Amberg-Unterammersricht", "Oberviechtach", "Kümmersbruck", "Nürnberg-Netzstall",
        "Waldmünchen", "Rothenburg ob der Tauber", "Schwandorf",
        "Weidenbach-Weiherschneidbach", "Roth", "Schorndorf-Knöbling",
        "Feuchtwangen-Heilbronn", "Parsberg-Eglwang/Oberpfalz", "Regensburg", "Zwiesel",
        "Weißenburg-Emetzheim", "Gelbelsee", "Eichstätt-Landershofen", "Metten",
        "Kösching", "Straubing", "Reimlingen", "Harburg", "Grainet-Rehberg",
        "Saldenburg-Entschenreuth", "Mallersdorf-Pfaffenberg-Oberlindhart",
        "Donauwörth-Osterweiler", "Ingolstadt-Manching", "Neuburg an der Donau",
        "Elsendorf-Horneck", "Gottfrieding", "Aldersbach-Kramersepp",
        "Dillingen/Donau-Fristingen", "Fürstenzell", "Günzburg",
        "Falkenberg (Kreis Rottal-Inn)", "Augsburg", "Altomünster-Maisbrunn",
        "Freising-Dürnast", "München (Flughafen)", "Neuburg/Kammel-Langenhaslach",
        "Mühldorf", "Simbach/Inn", "Maisach-Galgen", "Lechfeld", "München-Stadt",
        "Ebersberg-Halbing", "Trostberg", "Amerang-Pfaffing", "Oberhaching-Laufzorn",
        "Memmingen", "Chieming", "Wielenbach", "Holzkirchen", "Attenkam",
        "Kaufbeuren-Oberbeuren", "Siegsdorf-Höll", "Altenstadt", "Hohenpeißenberg",
        "Piding", "Kempten", "Bad Kohlgrub", "Oy-Mittelberg-Petersthal",
        "Kiefersfelden-Gach", "Schönau am Königssee", "Sigmarszell",
        "Garmisch-Partenkirchen", "Mittenwald", "Oberstdorf",
    ),
    "Berlin": (
        "Berlin-Buch", "Berlin-Marzahn", "Berlin-Tempelhof", "Berlin-Dahlem",
    ),
    "Brandenburg": (
        "Grünow", "Wittstock-Rote Mühle", "Stechlin-Menz", "Lenzen/Elbe", "Angermünde",
        "Zehdenick", "Neuruppin-Alt Ruppin", "Kyritz", "Heckelberg", "Berge",
        "Manschnow", "Müncheberg", "Potsdam", "Berlin Brandenburg (Flughafen)",
        "Wusterwitz", "Lindenberg", "Wiesenburg", "Baruth", "Coschen",
        "Lübben-Blumenfelde", "Langenlipsdorf", "Cottbus", "Holzdorf-Bernsdorf",
        "Doberlug-Kirchhain", "Schipkau-Klettwitz",
    ),
    "Bremen": (
        "Bremerhaven", "Bremen (Flughafen)",
    ),
    "Hamburg": (
        "Hamburg (Flughafen)", "Hamburg-Neuwiedenthal",
    ),
    "Hessen": (
        "Wesertal-Lippoldsberg", "Twistetal-Mühlhausen", "Schauenburg-Elgershausen",
        "Eschwege", "Fritzlar/Eder", "Sontra", "Burgwald-Bottendorf",
        "Gilserberg-Moischeid", "Neukirchen-Hauptschwenda", "Bad Hersfeld", "Cölbe",
        "Neu-Ulrichstein", "Alsfeld-Eifa", "Tann/Rhön", "Wettenberg bei Gießen",
        "Fulda-Horas", "Löhnberg-Obershausen", "Hoherodskopf/Vogelsberg", "Wasserkuppe",
        "Runkel-Ennerich", "Bad Nauheim", "Schlüchtern-Herolz", "Gründau-Breitenborn",
        "Waldems-Reinborn", "Kleiner Feldberg/Taunus", "Wiesbaden-Auringen",
        "Frankfurt/Main-Westend", "Offenbach-Wetterpark", "Frankfurt (Flughafen)",
        "Geisenheim", "Schaafheim-Schlierbach", "Darmstadt", "Michelstadt-Vielbrunn",
        "Michelstadt", "Oberzent-Beerfelden",
    ),
    "Mecklenburg-Vorpommern": (
        "Arkona", "Insel Hiddensee", "Putbus", "Barth", "Steinhagen-Negast",
        "Greifswalder Oie", "Rostock-Warnemünde", "Karlshagen", "Greifswald",
        "Sanitz-Groß Lüsewitz", "Tribsees", "Boltenhagen", "Kirchdorf/Poel",
        "Laage-Kronskamp", "Anklam", "Gülzow-Prüzen", "Teterow", "Ueckermünde",
        "Schwerin", "Goldberg", "Trollenhagen", "Waren (Müritz)", "Boizenburg",
        "Grambow-Schwennenz", "Marnitz", "Feldberg/Mecklenburg",
    ),
    "Niedersachsen": (
        "Cuxhaven", "Freiburg/Elbe", "Nordholz-Wanhöden", "Norderney",
        "Steinau (Kreis Cuxhaven)", "Wangerland-Hooksiel", "Borkum",
        "Mittelnkirchen-Hohenfelde", "Wittmundhafen", "Bremervörde", "Emden",
        "Rosengarten-Klecken", "Worpswede-Hüttenbusch", "Wendisch Evern",
        "Rotenburg/Wümme", "Friesoythe-Altenoythe", "Lüchow", "Soltau", "Dörpen",
        "Uelzen", "Großenkneten", "Faßberg", "Bassum", "Bergen", "Groß Berßen",
        "Meppen", "Wittingen-Vorhop", "Celle", "Diepholz", "Lingen-Baccum", "Alfhausen",
        "Hannover (Flughafen)", "Wunstorf", "Barsinghausen-Hohenbostel", "Belm",
        "Braunschweig", "Bückeburg", "Algermissen-Groß Lobke", "Helmstedt-Emmerstedt",
        "Hameln-Hastenbeck", "Alfeld", "Seesen", "Bad Harzburg",
        "Bevern (Kreis Holzminden)", "Braunlage", "Moringen-Lutterbeck", "Herzberg",
        "Göttingen",
    ),
    "Nordrhein-Westfalen": (
        "Rahden-Kleinendorf", "Münster/Osnabrück (Flughafen)", "Bad Salzuflen", "Ahaus",
        "Bielefeld-Deppendorf", "Borken in Westfalen", "Lügde-Paenbruch",
        "Ennigerloh-Ostenfelde", "Bad Lippspringe", "Lüdinghausen-Brochtrup", "Kleve",
        "Lippstadt-Bökenförde", "Waltrop-Abdinghof", "Werl", "Duisburg-Baerl",
        "Warburg", "Bochum", "Geldern-Walbeck", "Arnsberg-Neheim", "Brilon-Thülen",
        "Essen-Bredeney", "Gevelsberg-Oberbröking", "Düsseldorf (Flughafen)",
        "Tönisvorst", "Eslohe", "Lüdenscheid", "Wuppertal-Buchenhofen", "Kahler Asten",
        "Lennestadt-Theten", "Mönchengladbach-Hilderath", "Meinerzhagen-Redlendorf",
        "Reichshof-Eckenhagen", "Bad Berleburg-Stünzel", "Geilenkirchen-Neutevern",
        "Köln/Bonn (Flughafen)", "Neunkirchen-Seelscheid-Krawinkel",
        "Nörvenich-Niederbolheim", "Aachen-Orsbach", "Königswinter-Heiderhof",
        "Weilerswist-Lommersum", "Nideggen-Schmidt", "Kall-Sistig",
    ),
    "Rheinland-Pfalz": (
        "Hilgenroth", "Bad Marienberg", "Hümmerich", "Bad Neuenahr-Ahrweiler",
        "Montabaur", "Andernach", "Nürburg-Barweiler", "Schneifelforsthaus", "Büchel",
        "Manderscheid", "Blankenrath", "Wahlbach bei Simmern", "Mainz-Lerchenberg",
        "Hahn", "Olsdorf", "Bad Kreuznach", "Deuselbach", "Trier-Petrisberg", "Trier",
        "Alzey", "Idar-Oberstein", "Ruppertsecken", "Worms", "Bad Dürkheim",
        "Kaiserslautern", "Weinbiet", "Pirmasens", "Bad Bergzabern",
    ),
    "Saarland": (
        "Weiskirchen/Saar", "Perl-Nennig", "Tholey", "Neunkirchen-Wellesweiler",
        "Berus", "Saarbrücken-Burbach", "Saarbrücken (Flughafen)",
    ),
    "Sachsen": (
        "Bad Muskau", "Klitzschen bei Torgau", "Hoyerswerda",
        "Leipzig/Halle (Flughafen)", "Leipzig-Holzhausen", "Oschatz", "Görlitz",
        "Kubschütz", "Klipphausen-Garsebach", "Dresden-Klotzsche (Flughafen)",
        "Geringswalde-Altgeringswalde", "Sohland/Spree", "Nossen", "Dresden-Hosterwitz",
        "Lichtenhain-Mittelndorf", "Dippoldiswalde-Reinberg", "Bertsdorf-Hörnitz",
        "Chemnitz", "Zinnwald-Georgenfeld", "Lichtentanne", "Marienberg",
        "Deutschneudorf-Brüderwiese", "Aue", "Treuen", "Plauen", "Carlsfeld",
        "Bad Elster-Sohl",
    ),
    "Sachsen-Anhalt": (
        "Seehausen", "Gardelegen", "Demker", "Genthin", "Möckern-Drewitz", "Ummendorf",
        "Magdeburg", "Huy-Pabstorf", "Wittenberg", "Wernigerode", "Bernburg/Saale",
        "Quedlinburg", "Wernigerode-Schierke", "Köthen (Anhalt)",
        "Aschersleben-Mehringen", "Jeßnitz", "Oberharz am Brocken-Stiege", "Harzgerode",
        "Bad Lauchstädt", "Querfurt-Lodersleben", "Naumburg-Kreipitzsch/Saale",
        "Osterfeld", "Zeitz",
    ),
    "Schleswig-Holstein": (
        "List auf Sylt", "Glücksburg-Meierwik", "Leck", "Brodersby-Schönhagen",
        "Fehmarn", "Schleswig", "Hattstedt", "Schleswig-Jagel", "Kiel-Holtenau",
        "Sankt Peter-Ording", "Hohwacht", "Ostenfeld (Rendsburg)", "Hohn", "Erfde",
        "Helgoland", "Dörnick", "Pelzerhaken", "Elpersbüttel", "Wacken", "Padenstedt",
        "Hasenkrug-Hardebek", "Itzehoe", "Wittenborn", "Lübeck-Blankensee", "Quickborn",
        "Grambek",
    ),
    "Thüringen": (
        "Leinefelde", "Artern", "Sondershausen", "Mühlhausen-Görmar/Thüringen",
        "Olbersleben", "Dachwig", "Weimar-Schöndorf", "Eisenach",
        "Erfurt-Weimar (Flughafen)", "Starkenberg-Tegkwitz", "Jena",
        "Bad Berka (Flugplatz)", "Waltershausen", "Gera-Leumnitz", "Kleiner Inselsberg",
        "Salzungen, Bad-Gräfen-Nitzendorf", "Martinroda", "Schmieritz-Weltwitz",
        "Krölpa-Rockendorf", "Langenwetzendorf-Göttendorf", "Schmücke", "Schwarzburg",
        "Schleiz", "Meiningen", "Birx/Rhön", "Neuhaus am Rennweg", "Bad Lobenstein",
        "Veilsdorf",
    ),
}
