json2qgs
========

Lastenheft: https://github.com/simi-so/simi/blob/master/mp/kp/k2/K2_QgsTrafoLastenheft.md#qgstrafo


Konfiguration
-------------

### WMS / Print

* [JSON Schema](./schemas/sogis-wms-qgs-content.json)
* generiertes WMS-Projekt: `somap.qgs`
* generiertes Print-Projekt: `somap_print.qgs`

<details>
  <summary>Beispielkonfiguration</summary>

**Zu beachten:** Falls `print_templates` in der Config enthalten ist, wird automatisch das Print-Projekt (`somap_print.qgs`) generiert, sonst das WMS-Projekt (`somap.qgs`)

```jsonc
{
  "$schema": "https://github.com/simi-so/json2qgs/raw/master/schemas/sogis-wms-qgs-content.json",

  // top-level WMS Layers direkt unterhalb WMS Root Layer
  "wms_top_layers": [
    "ch.so.agi.agi_hoheitsgrenzen_pub.hoheitsgrenzen_gemeindegrenze",
    "Grundstücke",
    "BelasteteStandorte",
    "ch.so.agi.uebersichtsplan",
    "1_hintergrundkarte_wms",
    "2_hintergrundkarte_wmts"
  ],

  // referenzierte Layer und Productsets
  "layers": [
    // Productset: Layergruppe oder Facadelayer
    {
      "name": "Grundstücke",
      "type": "productset",
      "title": "Grundstücke",
      // Referenzen auf Sublayer
      "sublayers": [
        "mopublic_grundstueck"
      ]
    },
    {
      "name": "BelasteteStandorte",
      "type": "productset",
      "title": "",
      "sublayers": [
        "afu_altlasten_pub"
      ]
    },

    // Vektorlayer
    {
      "name": "ch.so.agi.agi_hoheitsgrenzen_pub.hoheitsgrenzen_gemeindegrenze",
      "type": "layer",
      "title": "Gemeindegrenzen",
      "datatype": "vector",
      // Datenquelle
      "postgis_datasource": {
        // PostGIS Connection wie in einer QGIS Datasource (hier als PG Service)
        "dbconnection": "service=sogis_services",
        // Variante ohne PG Service:
        // "dbconnection": "dbname='somap' host=sogis-postgis port=5432 user='dbuser' password='xxxx'",
        "schema": "agi_hoheitsgrenzen_pub",
        "table": "hoheitsgrenzen_gemeindegrenze",
        "unique_key": "t_id",
        "geometry_field": "geometrie",
        "geometry_type": "MULTIPOLYGON",
        "srid": 2056
      },
      // QML und zugehörige Assets mit Base64 Encoding
      "qml_base64": "ABCD123=",
      "qml_assets": [
        {
          // Asset Pfad relativ zum QGIS Projekt
          "path": "fillpattern/myCrossPattern.png",
          "base64": "EFGH456="
        }
      ],
      // Attribute und deren Aliases (Alias optional)
      "attributes": [
        {
          "name": "gemeindename",
          "alias": "Gemeindename"
        },
        {
          "name": "bfs_gemeindenummer",
          "alias": "BFS-Nr."
        },
        {
          "name": "bezirksname",
          "alias": "Bezirksname"
        }
      ],
      // BBox des Layers
      "bbox": {
        "bounds": [
          2592560.719,
          1213703.19,
          2644759.746,
          1261330.177
        ],
        "srid": 2056
      }
    },
    // analog:
    //  "mopublic_grundstueck",
    //  "afu_altlasten_pub"

    // Rasterlayer
    {
      "name": "ch.so.agi.uebersichtsplan",
      "type": "layer",
      "title": "Übersichtsplan",
      "datatype": "raster",
      // Datenquelle
      "raster_datasource": {
        "datasource": "/geodata/ch.so.agi.uebersichtsplanuebersichtsplan.vrt",
        "srid": 2056
      },
      // Raster QML mit Base64 Encoding
      "qml_base64": "MNOP012=",
      // BBox des Layers
      "bbox": {
        "bounds": [
          2590983.475,
          1212806.1156,
          2646267.025,
          1262755.0094
        ],
        "srid": 2056
      }
    },

    // WMS Layer (v.a. als interner Print Layer für Hintergrundkarte)
    {
      "name": "1_hintergrundkarte_wms",
      "type": "layer",
      "title": "Swisstopo Landeskarten (farbig) WMS",
      "datatype": "wms",
      // Datenquelle
      "wms_datasource": {
        "wms_url": "https://wms.geo.admin.ch/",
        "layers": "ch.swisstopo.pixelkarte-farbe",
        "format": "image/jpeg",
        "styles": "",
        "srid": 2056,
        "featureCount": 10
      },
      // BBox des Layers
      "bbox": {
        "bounds": [
          2590983.475,
          1212806.1156,
          2646267.025,
          1262755.0094
        ],
        "srid": 2056
      }
    },

    // WMTS Layer (v.a. als interner Print Layer für Hintergrundkarte)
    {
      "name": "2_hintergrundkarte_wmts",
      "type": "layer",
      "title": "Swisstopo Landeskarten (grau) WMTS",
      "datatype": "wmts",
      // Datenquelle
      "wmts_datasource": {
        "wmts_capabilities_url": "https://wmts.geo.admin.ch/EPSG/2056/1.0.0/WMTSCapabilities.xml",
        "layer": "ch.swisstopo.pixelkarte-grau",
        "style": "ch.swisstopo.pixelkarte-grau",
        // tile_dimensions ist üblicherweise leer, beim Swisstopo WMTS muss aber Time gesetzt werden
        "tile_dimensions": "Time=current",
        "tile_matrix_set": "2056_27",
        "srid": 2056,
        "format": "image/jpeg"
      },
      // BBox des Layers
      "bbox": {
        "bounds": [
          2590983.475,
          1212806.1156,
          2646267.025,
          1262755.0094
        ],
        "srid": 2056
      }
    }
  ],

  // Print Templates (nur für Print-Projekt)
  "print_templates": [
    {
      // QPT und zugehörige Assets mit Base64 Encoding
      "template_base64": "QRST345=",
      "template_assets": [
        {
          // Asset Pfad relativ zum QGIS Projekt
          "path": "logos/myPrintLogo.png",
          "base64": "UVWX678="
        }
      ]
    }
  ],

  // Farbe für Selektion im WMS
  "selection_color_rgba": [
    255, 255, 0, 255
  ],

  // WMS Metadaten
  "wms_metadata": {
    // WMS GetCapabilities
    "service_name": "",
    "service_title": "",
    "service_abstract": "",
    "keywords": [
      "somap"
    ],
    "online_resource": "",
    "contact_person": "",
    "contact_organization": "",
    "contact_position": "",
    "contact_phone": "",
    "contact_mail": "",
    "fees": "",
    "access_constraints": "",
    // Name und Titel des WMS Root Layers
    "root_name": "somap",
    "root_title": "",
    // Liste der angebotenen Referenzsysteme
    "crs_list": [
      "EPSG:2056"
    ],
    // gesamte BBox / Default BBox für Layer
    "bbox": {
      "bounds": [
        2590983,
        1212806,
        2646267,
        1262755
      ],
      "srid": 2056
    }
  }
}
```
</details>


### WFS

* [JSON Schema](./schemas/sogis-wfs-qgs-content.json)
* generiertes WFS-Projekt: `somap_wfs.qgs`

<details>
  <summary>Beispielkonfiguration</summary>

```jsonc
{
  "$schema": "https://github.com/simi-so/json2qgs/raw/master/schemas/sogis-wfs-qgs-content.json",

  // WFS Layerliste
  "layers": [
    // Vektorlayer
    {
      "name": "ch.so.agi.agi_hoheitsgrenzen_pub.hoheitsgrenzen_gemeindegrenze",
      "title": "Gemeindegrenzen",
      // Datenquelle
      "postgis_datasource": {
        // PostGIS Connection wie in einer QGIS Datasource (hier als PG Service)
        "dbconnection": "service=sogis_services",
        // Variante ohne PG Service:
        // "dbconnection": "dbname='somap' host=sogis-postgis port=5432 user='dbuser' password='xxxx'",
        "schema": "agi_hoheitsgrenzen_pub",
        "table": "hoheitsgrenzen_gemeindegrenze",
        "unique_key": "t_id",
        "geometry_field": "geometrie",
        "geometry_type": "MULTIPOLYGON",
        "srid": 2056
      },
      // Attribute und deren Aliases (Alias optional)
      "attributes": [
        {
          "name": "gemeindename",
          "alias": "Gemeindename"
        },
        {
          "name": "bfs_gemeindenummer",
          "alias": "BFS-Nr."
        },
        {
          "name": "bezirksname",
          "alias": "Bezirksname"
        }
      ],
      // BBox des Layers
      "bbox": {
        "bounds": [
          2592560.719,
          1213703.19,
          2644759.746,
          1261330.177
        ],
        "srid": 2056
      }
    }
  ],
  // WFS Metadaten
  "wfs_metadata": {
    // WFS GetCapabilities
    "service_name": "",
    "service_title": "",
    "service_abstract": "",
    "keywords": [
      "somap"
    ],
    "online_resource": "",
    "fees": "",
    "access_constraints": "",
    // Default BBox für Layer
    "bbox": {
      "bounds": [
        2590983,
        1212806,
        2646267,
        1262755
      ],
      "srid": 2056
    }
  }
}
```
</details>


Benutzung
---------

### Kommandozeilenparameter

```
usage: json2qgs.py [-h] [--qgsTemplateDir [QGSTEMPLATEDIR]] [--log_level [{info,debug}]] qgsContent {wms,wfs} destination {2,3}

positional arguments:
  qgsContent            Path to qgsContent config file
  {wms,wfs}             Availabel modes: wms, wfs
  destination           Directory where the generated QGS and QML assets should be saved in
  {2,3}                 Wether to use the QGIS 2 or QGIS 3 service template

optional arguments:
  -h, --help            show this help message and exit
  --qgsTemplateDir [QGSTEMPLATEDIR]
                        Path to template directory
  --log_level [{info,debug}]
                        Specifies the log level

```

### Skript

Alle Befehle anzeigen:

    python json2qgs.py --help

WMS-Projekt generieren (für WMS oder Print):

    python json2qgs.py demo-config/qgsContentWMS.json wms ./ 3

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

    python json2qgs.py demo-config/qgsContentWMS.json wms ./ 3
    python json2qgs.py demo-config/qgsContentPrint.json wms ./ 3
    python json2qgs.py demo-config/qgsContentWFS.json wfs ./ 3
