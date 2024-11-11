from xml.dom import minidom
from typing import List, Optional, Type
import inspect

class XmlUtils:

    @staticmethod
    def tokenize_path(path: str) -> List[str]:
        """Splits the path by periods (".") into components."""
        return path.split(".")

    @staticmethod
    def parse_xml(stream) -> Optional[minidom.Document]:
        """Parses an XML document from an input stream."""
        try:
            doc = minidom.parse(stream)
            doc.documentElement.normalize()
            return doc
        except Exception as e:
            print(f"Error parsing XML: {e}")
            return None

    @staticmethod
    def get_elements(from_node, tag: str) -> List[minidom.Node]:
        """Returns all elements with a specific tag from a document or node."""
        elements = []
        
        if isinstance(from_node, minidom.Document):
            elements = from_node.getElementsByTagName(tag)
        elif isinstance(from_node, minidom.Node):
            for child in from_node.childNodes:
                if child.nodeName == tag:
                    elements.append(child)
        return elements

    @staticmethod
    def first_element(start: minidom.Node, tag: str) -> Optional[minidom.Node]:
        """Returns the first element with the specified tag, or None if not found."""
        elements = XmlUtils.get_elements(start, tag)
        return elements[0] if elements else None

    @staticmethod
    def get_attr_value(node: minidom.Node, attr: str) -> Optional[str]:
        """Gets the attribute value of an element node."""
        if isinstance(node, minidom.Element):
            return node.getAttribute(attr)
        return None

    @staticmethod
    def select(from_node: minidom.Node, path: str) -> List[minidom.Node]:
        """Selects nodes based on a path of tags separated by periods."""
        tags = XmlUtils.tokenize_path(path)
        for tag in tags[:-1]:
            from_node = XmlUtils.first_element(from_node, tag)
            if from_node is None:
                return []
        return XmlUtils.get_elements(from_node, tags[-1])

    @staticmethod
    def select_first(from_node: minidom.Node, path: str) -> Optional[minidom.Node]:
        """Selects the first node that matches the specified path."""
        nodes = XmlUtils.select(from_node, path)
        return nodes[0] if nodes else None

    @staticmethod
    def get_value(node: minidom.Node) -> str:
        """Gets the text content of a node."""
        return node.firstChild.nodeValue.strip() if node and node.firstChild else ""

    @staticmethod
    def get_value_by_path(from_node: minidom.Node, path: str) -> Optional[str]:
        """Gets the text content of the first node matching the specified path."""
        node = XmlUtils.select_first(from_node, path)
        return XmlUtils.get_value(node) if node else None

    @staticmethod
    def fill_instance(instance: object, clazz: Type, node: minidom.Node):
        """Populates the fields of an instance with XML attribute values."""
        for name, field in inspect.getmembers(clazz, lambda f: isinstance(f, property) or not callable(f)):
            if name.startswith("att"):
                attr_name = name[3:]  # Remove "att" prefix
                value = XmlUtils.get_attr_value(node, attr_name)
                if value is not None:
                    setattr(instance, name, value)

    @staticmethod
    def instance_from_node(clazz: Type, node: minidom.Node) -> Optional[object]:
        """Creates an instance of a class and populates it with XML data."""
        try:
            instance = clazz()
            current_class = clazz
            while current_class:
                XmlUtils.fill_instance(instance, current_class, node)
                current_class = current_class.__base__
            return instance
        except Exception as e:
            print(f"Error creating instance from XML node: {e}")
            return None


# from io import StringIO

# xml_data = """
# <root>
#     <item attName="ExampleName" attValue="ExampleValue">
#         <child attSubName="SubExample"/>
#     </item>
# </root>
# """

# # Parse XML from a string
# stream = StringIO(xml_data)
# document = XmlUtils.parse_xml(stream)

# # Access elements and attributes
# item = XmlUtils.first_element(document, "item")
# print(XmlUtils.get_attr_value(item, "attName"))  # Should print "ExampleName"

# # Get the value of a nested element by path
# print(XmlUtils.get_value_by_path(document, "item.child"))  # Access text in <child> if present
