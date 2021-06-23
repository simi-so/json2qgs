from json2qgs import Json2Qgs, Logger
from collections import OrderedDict
from xml.etree import ElementTree

import unittest
import json
import requests
import logging
import os
import shutil
import itertools


class CapabilitiesTest(unittest.TestCase):
    """Test case for the generation of qgis projects"""

    def test_generated_qgis_projects(self):
        """Test whether the capabilities of the generated QGIS project has
           included the same layers as defined in the json2qgs config.
        """
        qgis_version_to_test = [2, 3]
        modes_to_test = ["print", "wfs"]
        template_path = "qgs/"
        qgis_server_url = os.getenv(
                "QGIS_SERVER_URL",
                "http://127.0.0.1:8001/ows").rstrip("/")
        qgis_server_path = os.getenv(
                "PATH_TO_QGIS_SERVER_DIRECTORY",
                "tests/docker/volumes/qgs-resources/")
        # Destination path of json2qgs
        # Path where the QGS will be generated
        dest_path = "tests/"

        for qgis_version, mode in list(itertools.product(
                qgis_version_to_test, modes_to_test)):

            if mode == "print":
                config_path = "demo-config/qgsContentPrint.json"
            else:
                config_path = "demo-config/qgsContentWFS.json"

            # Generate project and get the used json2qgs config
            config = self.generate_qgis_project(
                config_path, mode, qgis_version, template_path)
            layers_from_config = []

            # Copy the generated project to qgis server
            qgis_project_path = os.path.join(
                qgis_server_path, "somap_%s.qgs" % mode)
            shutil.move(os.path.join(
                dest_path, "somap_%s.qgs" % mode), qgis_project_path)

            # Get all layer names from json2qgs config
            for layer in config["layers"]:
                layers_from_config.append(layer["name"])

            # Get all layer names from capabilities of the generated project
            layers_from_capbilities = self.get_layer_list_from_capabilities(
                qgis_server_url + "/somap_%s" % mode,
                "wms" if mode == "print" else "wfs")

            # Delete copied file
            os.remove(qgis_project_path)

            # Compare the two layer name lists
            self.assertCountEqual(layers_from_capbilities, layers_from_config)

    def generate_qgis_project(self, config_path, mode,
                              qgis_version, template_path):
        """Generate a qgis project with json2qgs

        Args:
            config_path (str): Json2Qgs config path
            mode (str): Project type: [wms | wfs]
            qgis_version (int): Define the version of the QGIS template to use
            template_path (str): Path to the qgs template dir where the
                                 default QMLs and QGIS template files
                                 should exist

        Returns:
            dict: json2qgs config
        """

        # read Json2Qgs config file
        try:
            with open(config_path) as f:
                # parse config JSON with original order of keys
                config = json.load(f, object_pairs_hook=OrderedDict)
        except Exception as e:
            print("Error loading qgsContent JSON:\n%s" % e)
            exit(1)

        generator = Json2Qgs(
            config,
            Logger("Json2Qgs", logging.INFO),
            "tests/",
            qgis_version,
            template_path,
            "somap"
        )

        if mode == 'print':
            generator.generate_wms_project()
        elif mode == 'wfs':
            generator.generate_wfs_project()

        return config

    def get_layer_list_from_capabilities(self, url, service_type):
        """Get list of all layer names from capabilities

        Args:
            url (str): url to capabilities
            service_type (str): [wms | wfs]

        Returns:
            list: str list of layer names
        """

        response = requests.get(
            url,
            params={
                'SERVICE': service_type.upper(),
                'VERSION': '1.3.0',
                'REQUEST': 'GetCapabilities'
            },
            timeout=60
        )

        # parse GetCapabilities XML
        ElementTree.register_namespace(
            '', 'http://www.opengis.net/%s' % service_type)
        ElementTree.register_namespace('qgs', 'http://www.qgis.org/wms')
        ElementTree.register_namespace('sld', 'http://www.opengis.net/sld')
        ElementTree.register_namespace(
            'xlink', 'http://www.w3.org/1999/xlink'
        )

        xml_root = ElementTree.fromstring(response.content)

        # use default namespace for XML search
        # namespace dict
        ns = {'ns': 'http://www.opengis.net/%s' % service_type}
        # namespace prefix
        np = 'ns:'
        if not xml_root.tag.startswith('{http://'):
            # do not use namespace
            ns = {}
            np = ''

        if service_type == "wms":
            root_layer = xml_root.find('%sCapability/%sLayer' % (np, np), ns)

            return self.collect_wms_layers(root_layer, [], np, ns)
        else:
            return [xml_root.find('%sFeatureTypeList/%sFeatureType/%sName' % (np, np, np), ns).text]

    def collect_wms_layers(self, layer, layers_list, np, ns):
        """Get layer names recursivly

        Args:
            layer (ElementTree.Element): Layer/Group to add
            layers_list (list): List of the found layer names
            np (str): np
            ns (dict): ns

        Returns:
            [list]: List of all layer names
        """

        for sub_layer in layer.findall('%sLayer' % np, ns):
            layer_name = sub_layer.find('%sName' % np, ns).text

            if layer_name is not None:
                layers_list.append(layer_name)

                layers_list = self.collect_wms_layers(
                    sub_layer, layers_list, np, ns)

        return layers_list
