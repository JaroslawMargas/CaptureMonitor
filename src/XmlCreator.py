import logging
import datetime
import re
import os
import xml.etree.ElementTree as ETree

module_logger = logging.getLogger('application.XmlCreator')


def get_element_list(path_file, child_tag, element_tag):
    r_tree = ETree.parse(path_file)
    r_root = r_tree.getroot()
    element_list = []
    for child in r_root.findall(child_tag):
        arg_list = []
        for params in child.findall(element_tag):
            if params.attrib.get('name') == "time":
                arg_list.append(float(params.text))
            else:
                arg_list.append(int(params.text))
        element_list.append(arg_list)
    return element_list


def merge_files(search_path, child_tag, element_tag):
    merged_list = []
    for expected_file in os.listdir(search_path):
        if expected_file.endswith(".xml"):
            tmp = get_element_list(expected_file, child_tag, element_tag)
            merged_list += tmp
    return merged_list


class XmlCreator(object):

    def __init__(self):
        self.r_root = None
        self.logger = logging.getLogger('application.XmlCreator')
        self.logger.debug('creating an instance of XmlCreator')
        self.root = None
        self.child = None
        self.tree = None

    def create_root(self, root_tag):
        self.root = ETree.Element(root_tag)

    def create_child(self, child_tag):
        self.child = ETree.SubElement(self.root, child_tag)

    def create_element(self, element_tag, name, value):
        ETree.SubElement(self.child, element_tag, name=name).text = value

    def compose_tree(self):
        self.tree = ETree.ElementTree(self.root)

    def save_xml(self):
        filename = str(datetime.datetime.now())
        filename = re.sub(":", "", filename) + '.xml'
        self.tree.write(filename)


