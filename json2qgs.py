from collections import OrderedDict
from datetime import datetime
from xml.dom.minidom import parseString
from jinja2 import Template

import argparse
import json
import os
import base64
import html
import uuid
import re
import requests
import jsonschema


class Logger():
    """Simple logger class"""
    def debug(self, msg):
        print("[%s] \033[36mDEBUG: %s\033[0m" % (self.timestamp(), msg))

    def info(self, msg):
        print("[%s] INFO: %s" % (self.timestamp(), msg))

    def warning(self, msg):
        print("[%s] \033[33mWARNING: %s\033[0m" % (self.timestamp(), msg))

    def error(self, msg):
        print("[%s] \033[31mERROR: %s\033[0m" % (self.timestamp(), msg))

    def timestamp(self):
        return datetime.now()


class Json2Qgs():
    """Json2Qgs class

    Generate QGS and QML files from a JSON config file.
    """

    def __init__(self, config, logger, dest_path):
        """Constructor

        :param obj config: Json2Qgs config
        :param Logger logger: Logger
        :param str dest_path: Path where the generated files should be saved
        """
        self.logger = logger

        self.config = config

        # get config settings
        self.project_output_dir = dest_path
        self.default_extent = config.get(
            'wms_metadata', {}).get("bbox", {}).get("bounds", None)
        self.selection_color = config.get(
            'selection_color_rgba', [255, 255, 0, 255]
        )

        # load default styles
        self.default_styles = {
            "point": self.load_template('qgs/point.qml'),
            "linestring": self.load_template('qgs/linestring.qml'),
            "polygon": self.load_template('qgs/polygon.qml'),
            "raster": self.load_template('qgs/raster.qml')
        }

        self.wms_top_layer = config.get("wms_top_layers", [])

    def load_template(self, path):
        """Load contents of QGIS template file.

        :param str path: Path to template file
        """
        template = None
        try:
            # get absolute path to template
            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), path)
            )
            with open(path) as f:
                template = f.read()
        except Exception as e:
            self.logger.error("Error loading template file '%s':\n%s" % (path, e))

        return template

    def parse_qml_style(self, xml, attributes=[]):
        """ Parse QML and set aliases
        """
        doc = parseString(xml)
        qgis = doc.getElementsByTagName("qgis")[0]
        attr = " ".join(['%s="%s"' % entry for entry in filter(
            lambda entry: entry[0] != "version", qgis.attributes.items())])

        # update aliases
        if attributes:
            aliases = qgis.getElementsByTagName("aliases")
            if not aliases:
                # create <aliases>
                aliases = doc.createElement("aliases")
            else:
                # get <aliases>
                aliases = aliases[0]

            # remove existing aliases
            for alias in list(aliases.childNodes):
                aliases.removeChild(alias)

            # add aliases from layer config
            for i, attribute in enumerate(attributes):
                # get alias from from alias data
                attr_alias = attribute.get("alias", "")
                try:
                    if attr_alias.startswith('{'):
                        # parse JSON
                        json_config = json.loads(attr_alias)
                        attr_alias = json_config.get('alias', attr_alias)
                except Exception as e:
                    self.logger.warning(
                        "Could not parse value as JSON: '%s'\n%s" %
                        (attr_alias, e)
                    )

                alias = doc.createElement("alias")
                alias.setAttribute('field', attribute["name"])
                alias.setAttribute('index', str(i))
                alias.setAttribute('name', attr_alias)
                aliases.appendChild(alias)

        style = "".join([node.toxml() for node in qgis.childNodes])
        return {"attr": attr, "style": style}

    def collect_layer(self, layer):
        """Collect layer info for layersubtree from qgsContent.

        param dict layer: Data layer dictionary
        """

        layer_keys = layer.keys()
        qgs_layer = {
            "name": html.escape(layer["name"]),
            "type": layer["type"],
            "title": html.escape(layer["title"]),
            "id": str(uuid.uuid4()),
            "layertype": layer["datatype"],
            "mapTip": "",
            "dataUrl": "",
            "abstract": "",
            }

        if "bbox" in layer_keys:
            qgs_layer["extent"] = layer["bbox"]["bounds"]
        else:
            qgs_layer["extent"] = self.default_extent

        if "postgis_datasource" in layer_keys:
            # datasource from the JSON config
            datasource = layer["postgis_datasource"]
            qgs_layer["provider"] = "postgres"
            qgs_layer["datasource"] = (
                "{db_connection} sslmode=disable key='{pkey}' srid={srid} "
                "type={geometry_type} table=\"{schema}\".\"{table}\" "
                "({geometry_column}) sql=".format(
                    db_connection=datasource["dbconnection"],
                    pkey=datasource["unique_key"],
                    srid=datasource["srid"],
                    geometry_type=datasource["geometry_type"],
                    schema=datasource["schema"],
                    table=datasource["table"],
                    geometry_column=datasource["geometry_field"]
                    )
                )
            try:
                qml = self.get_qml_from_base64(
                    layer["qml_base64"], layer.get("attributes", []))
                qgs_layer["style"] = qml["style"]
                qgs_layer["attributes"] = qml["attr"]

            except:
                self.logger.warning(
                    "Falling back to default style for %s" % layer["name"])

                singletype = re.sub(
                    '^multi', "", datasource["geometry_type"].lower())
                qml = self.parse_qml_style(
                    self.default_styles[singletype],
                    layer.get("attributes", []))
                qgs_layer["style"] = qml["style"]
                qgs_layer["attributes"] = qml["attr"]

            if "qml_assets" in layer_keys:
                # Iterate through all assets used in the QML and save them
                # in the filesystem
                # If the asset path defines directories that do not exist,
                # then create those directories and save the asset image
                # TODO: Do we need path protection here? Example: /etc/passwd
                for asset in layer["qml_assets"]:
                    try:
                        os.makedirs(
                            os.path.dirname(asset["path"]), exist_ok=True)
                        with open(asset["path"], "wb") as fh:
                            fh.write(
                                base64.b64decode(asset["base64"]))
                    except Exception as e:
                        self.logger.warning(
                            "[Layer: {}] An error occured when trying to save {}\n{}".format(
                                qgs_layer["name"], asset["path"], str(e)))

        elif "raster_datasource" in layer_keys:
            # TODO: srid is not used here?
            # datasource from the JSON config
            qgs_layer["provider"] = "gdal"
            qgs_layer["datasource"] = layer["raster_datasource"]["datasource"]

            try:
                qml = self.get_qml_from_base64(
                    layer["qml_base64"], layer.get("attributes", []))
                qgs_layer["style"] = qml["style"]
                qgs_layer["attributes"] = qml["attr"]

            except:
                self.logger.warning(
                    "Falling back to default style for %s" % layer["name"])

                qml = self.parse_qml_style(
                    self.default_styles["raster"],
                    layer.get("attributes", []))
                qgs_layer["style"] = qml["style"]
                qgs_layer["attributes"] = qml["attr"]

        elif "wms_datasource" in layer_keys:
            # Constant value
            datasource = html.escape("contextualWMSLegend=0&")
            datasource += html.escape(
                "crs=EPSG:%s&" % layer["wms_datasource"]["srid"])
            # Constant value
            datasource += html.escape("dpiMode=7&")
            datasource += html.escape(
                "featureCount=%s&" % layer["wms_datasource"].get(
                    "featureCount", 10))
            datasource += html.escape(
                "format=%s&" % layer["wms_datasource"]["format"])
            datasource += html.escape(
                "layers=%s&" % layer["wms_datasource"]["layers"])
            datasource += html.escape(
                "styles=%s&" % layer["wms_datasource"].get("styles", ""))
            datasource += html.escape(
                "url=%s" % layer["wms_datasource"]["wms_url"])

            qgs_layer["provider"] = "wms"
            qgs_layer["datasource"] = datasource
        elif "wmts_datasource" in layer_keys:
            # Constant value
            datasource = html.escape("contextualWMSLegend=0&")
            datasource += html.escape(
                "crs=EPSG:%s&" % layer["wmts_datasource"]["srid"])
            # Constant value
            datasource += html.escape("dpiMode=7&")
            # Constant value
            datasource += html.escape("featureCount=10&")
            datasource += html.escape(
                "format=%s&" % layer["wmts_datasource"]["format"])
            datasource += html.escape(
                "layers=%s&" % layer["wmts_datasource"]["layer"])
            datasource += html.escape(
                "styles=%s&" % layer["wmts_datasource"].get("style", ""))
            datasource += html.escape(
                "tileDimensions=%s&" % layer["wmts_datasource"].get(
                    "tile_dimensions", ""))
            datasource += html.escape(
                "tileMatrixSet=%s&" % layer["wmts_datasource"][
                    "tile_matrix_set"])
            datasource += html.escape(
                "url=%s" % layer["wmts_datasource"]["wmts_capabilities_url"])

            qgs_layer["provider"] = "wms"
            qgs_layer["datasource"] = datasource

        return qgs_layer

    def get_qml_from_base64(self, base64_qml, attributes):
        """Decode base64_qml with base64 and return the parsed qml style

        param str base64_qml: QML encoded with base64
        param list attributes: attributes list used to set aliases in the QML
        return dict {"attr": data, "style": data}
        """

        qml = base64.b64decode(base64_qml).decode("utf-8")
        return self.parse_qml_style(qml, attributes)

    def collect_wms_metadata(self, metadata, layertree, composers=[]):
        """Collect wms metadata from qgsContent

        param dict metadata: Metadata specified in qgsContent
        param list layertree: The whole QGS layer tree
        return dict bindings: Dict for jinja
        """
        # TODO: Where do we use this?
        wms_service_name = metadata.get('service_name', '')
        wms_online_resource = metadata.get('online_resource', '')

        wms_extent = metadata.get('bbox')
        if wms_extent:
            wms_extent = wms_extent['bounds']

        return {
                'wms_service_title': html.escape(
                    metadata.get('service_title', '')),
                'wms_service_abstract': html.escape(
                    metadata.get('service_abstract', '')),
                'wms_keywords': metadata.get('keywords', None),
                'wms_url': html.escape(wms_online_resource),
                'wms_contact_person': html.escape(
                    metadata.get('contact_person', '')),
                'wms_contact_organization': html.escape(
                    metadata.get('contact_organization', '')
                ),
                'wms_contact_position': html.escape(
                    metadata.get('contact_position', '')),
                'wms_contact_phone': html.escape(
                    metadata.get('contact_phone', '')),
                'wms_contact_mail': html.escape(
                    metadata.get('contact_mail', '')),
                'wms_fees': html.escape(metadata.get('fees', '')),
                'wms_access_constraints': html.escape(
                    metadata.get('access_constraints', '')),
                'wms_root_name': html.escape(
                    metadata.get('root_name', '')),
                'wms_root_title': html.escape(
                    metadata.get('root_title', '')),
                'wms_crs_list': metadata.get('crs_list', ['EPSG:2056']),
                'wms_extent': wms_extent,
                'layertree': layertree,
                'composers': composers,
                'selection_color': self.selection_color
            }

    def collect_group_layer(self, group_layer, layers):
        """Collect group layer info for layersubtree from qgsContent.

        param dict group_layer: group layer dictionary
        param list layers: Layer list, which is used to collect info
                           on sublayers.
        """
        sublayers = []

        for layer in layers:
            if layer["name"] in group_layer["sublayers"]:
                sublayers.append(self.collect_layer(layer))

        return {
            "type": group_layer["type"],
            "name": group_layer["name"],
            "title": group_layer["title"],
            "items": sublayers
        }

    def generate_wms_project(self, with_composers=False):
        """Generate project

        param bool with_composers: Wether to add the defined
                                   composers to the project
        """

        if os.path.exists(self.project_output_dir) is False:
            self.logger.error(
                "Destination directory ({}) does not exist!".format(
                    self.project_output_dir))
            return

        if self.validate_schema() is False:
            return

        qgis2_template = self.load_template("./qgs/service_2.qgs")
        layers = self.config.get("layers")

        composers = []
        layertree = []

        for layer in layers:
            if layer["name"] in self.wms_top_layer:
                if layer["type"] != 'productset':
                    layertree.append(self.collect_layer(layer))
                else:
                    layertree.append(
                        self.collect_group_layer(layer, layers))

        if with_composers:
            # Iterate through all assets used in the QTP and save them
            # in the filesystem
            # If the asset path defines directories that do not exist,
            # then create those directories and save the asset image
            # TODO: Do we need path protection here? Example: /etc/passwd
            for composer in self.config.get("print_templates", []):
                try:
                    composers.append(base64.b64decode(
                        composer["template_base64"]).decode("utf-8"))

                except:
                    self.logger.error(
                        "Error trying to decode print template!")

                for asset in composer.get("template_assets", []):
                    try:
                        os.makedirs(
                            os.path.dirname(asset["path"]), exist_ok=True)
                        with open(asset["path"], "wb") as fh:
                            fh.write(
                                base64.b64decode(asset["base64"]))
                    except Exception as e:
                        self.logger.warning(
                            "An error occured when trying to save {}\n{}".format(
                                asset["path"], str(e)))

        qgs_template = Template(qgis2_template)
        binding = self.collect_wms_metadata(self.config.get(
            "wms_metadata", {}), layertree, composers=composers)
        qgs = qgs_template.render(**binding)

        if with_composers is True:
            mode = "print"
        else:
            mode = "wms"

        qgs_path = os.path.join(self.project_output_dir, "somap_%s.qgs" % mode)

        try:
            with open(qgs_path, 'w', encoding='utf-8') as f:
                f.write(qgs)
                self.logger.debug("Wrote %s" % os.path.abspath(qgs_path))
        except PermissionError:
            self.logger.error(
                "PermissionError: Could not write %s" % os.path.abspath(
                    qgs_path))

    def validate_schema(self):
        """Validate config against its JSON schema.

        return bool valid : Return true if JSON config is valid
        """

        # download JSON schema
        response = requests.get(self.config["$schema"])
        if response.status_code != requests.codes.ok:
            self.logger.error(
                "Could not download JSON schema from %s:\n%s" %
                (self.config["$schema"], response.text)
            )
            return False

        # parse JSON
        try:
            schema = json.loads(response.text)
        except Exception as e:
            self.logger.error("Could not parse JSON schema:\n%s" % e)
            return False

        # validate against schema
        valid = True
        validator = jsonschema.validators.validator_for(schema)(schema)
        for error in validator.iter_errors(self.config):
            valid = False

            # collect error messages
            messages = [
                e.message for e in error.context
            ]
            if not messages:
                messages = [error.message]

            # collect path to concerned subconfig
            # e.g. ['resources', 'wms_services', 0]
            #      => ".resources.wms_services[0]"
            path = ""
            for p in error.absolute_path:
                if isinstance(p, int):
                    path += "[%d]" % p
                else:
                    path += ".%s" % p

            # get concerned subconfig
            instance = error.instance
            if isinstance(error.instance, dict):
                # get first level of properties of concerned subconfig
                instance = OrderedDict()
                for key, value in error.instance.items():
                    if isinstance(value, dict) and value.keys():
                        first_value_key = list(value.keys())[0]
                        instance[key] = {
                            first_value_key: '...'
                        }
                    elif isinstance(value, list):
                        instance[key] = ['...']
                    else:
                        instance[key] = value

            # log errors
            message = ""
            if len(messages) == 1:
                message = "Validation error: %s" % messages[0]
            else:
                message = "\nValidation errors:\n"
                for msg in messages:
                    message += "  * %s\n" % msg
            self.logger.error(message)
            self.logger.warning("Location: %s" % path)
            self.logger.warning(
                "Value: %s" %
                json.dumps(
                    instance, sort_keys=False, indent=2, ensure_ascii=False
                )
            )
        return valid


# command line interface
if __name__ == '__main__':
    print("Starting SO!GIS json2qgs...")

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'qgsContent', help="Path to qgsContent config file"
    )
    parser.add_argument(
        "mode", choices=['wms', 'prints', 'wfs'],
        help="Availabel modes: WMS/Print/WFS"
    )
    parser.add_argument(
        "destination",
        help="Directory where the generated QGS and QML assets should be saved in"
    )
    args = parser.parse_args()

    # read Json2Qgs config file
    try:
        with open(args.qgsContent) as f:
            # parse config JSON with original order of keys
            config = json.load(f, object_pairs_hook=OrderedDict)
    except Exception as e:
        print("Error loading qgsContent JSON:\n%s" % e)
        exit(1)

    # create logger
    logger = Logger()

    # create Json2Qgs
    generator = Json2Qgs(config, logger, args.destination)
    if args.mode == 'wms':
        generator.generate_wms_project()
    elif args.mode == 'prints':
        generator.generate_wms_project(with_composers=True)
    elif args.mode == 'wfs':
        pass
