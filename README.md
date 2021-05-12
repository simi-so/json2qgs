json2qgs
========

Lastenheft: https://github.com/simi-so/simi/blob/master/mp/kp/k2/K2_QgsTrafoLastenheft.md#qgstrafo


Benutzung
---------

### Kommandozeilenparameter

| Bezeichnung | Beschreibung | Beispiel |
|-------------|--------------|----------|
| qgsContent  | Pfad zu "qgsContent.json" |
| mode        | Der Modus beschreibt welche Art von Projekt generiert werden soll.<br> - `wms`: WMS-Projekt generieren (ohne print templates) <br> - `print`: WMS-Projekt generieren (mit print template) <br> - `wfs`: WFS-Projekt generieren  |
| destination | Pfad, unter welchem das erzeugte QGS abgelegt wird |
| qgisVersion | Ziel QGIS version des generierten Projekt. <br> - `2`: QGIS 2 <br> - `3`: QGIS 3 |

### Skript

Alle Befehle anzeigen:

    python json2qgs.py --help

WMS-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWMS.json wms ./

Print-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWMS.json print ./

WFS-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWFS.json wfs ./

Entwicklung
-----------

Erstellen einer virtuellen Umgebung:

    virtualenv --python=/usr/bin/python3 .venv

Virtuelle Umgebung aktivieren:

    source .venv/bin/activate

Anforderungen installieren:

    pip install -r requirements.txt

Erzeugen von QGIS-Projektdateien:

    python json2qgs.py demo-config/qgsContentWMS.json print .
