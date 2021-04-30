json2qgs
========

Lastenheft: https://github.com/simi-so/simi/blob/master/mp/kp/k2/K2_QgsTrafoLastenheft.md#qgstrafo


Benutzung
---------

### Skript

Alle Befehle anzeigen:

    python json2qgs.py --help

WMS-Projekt generieren:

    python json2qgs.py demo-config/qgsContentWMS.json wms ./

Print-Projekt generieren:

    python json2qgs.py demo-config/qgsContentPrint.json prints ./

Entwicklung
-----------

Erstellen einer virtuellen Umgebung:

    virtualenv --python=/usr/bin/python3 .venv

Virtuelle Umgebung aktivieren:

    source .venv/bin/activate

Anforderungen installieren:

    pip install -r requirements.txt

Erzeugen von QGIS-Projektdateien:

    python json2qgs.py demo-config/qgsContentPrint.json prints .
