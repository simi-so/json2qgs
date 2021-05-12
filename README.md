json2qgs
========

Lastenheft: https://github.com/simi-so/simi/blob/master/mp/kp/k2/K2_QgsTrafoLastenheft.md#qgstrafo


Benutzung
---------

### Kommandozeilenparameter

| Bezeichnung   | Beschreibung | Optional | Standardwert | Beispiel |
|---------------|--------------|----------|--------------|----------|
| qgsContent    | Pfad zu "qgsContent.json" | Nein | - | `demo-config/qgsContentWMS.json` |
| mode          | Der Modus beschreibt welche Art von Projekt generiert werden soll.<br> - `wms`: WMS-Projekt generieren (ohne print templates) <br> - `print`: WMS-Projekt generieren (mit print template) <br> - `wfs`: WFS-Projekt generieren | Nein | - | `wms` |
| destination   | Pfad, unter welchem das erzeugte QGS abgelegt wird | Nein | - | `./` |
| qgisVersion   | Ziel QGIS version des generierten Projekt. <br> Optionen: <br> - `2`: QGIS 2 <br> - `3`: QGIS 3 | Nein | - | `3` |
| qgsTemplateDir| Pfad zum Verzeichniss wo sich folgende template Dateien befinden müssen: <br> - `linestring.qml` <br> - `point.qml` <br> - `polygon.qml` <br> - `raster.qml` <br> - `service_2.qgs` <br> - `service_3.qgs` | Ja | `qgs/` | `--qgsTemplateDir qgs/` |
| log_level     | Log level <br> - `info` <br> - `debug` | Ja | `info` | `--log_level debug` |

### Skript

Alle Befehle anzeigen:

    python json2qgs.py --help

WMS-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWMS.json wms ./ 3

Print-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWMS.json print ./ 3

WFS-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWFS.json wfs ./ 3

Entwicklung
-----------

Erstellen einer virtuellen Umgebung:

    virtualenv --python=/usr/bin/python3 .venv

Virtuelle Umgebung aktivieren:

    source .venv/bin/activate

Anforderungen installieren:

    pip install -r requirements.txt

Erzeugen von QGIS-Projektdateien:

    python json2qgs.py demo-config/qgsContentWMS.json print . 3
