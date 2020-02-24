import tempfile
import os
import uuid
import lxml.etree as et
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from .util import is_url, get_service_cap_key
import urllib.parse as urlparse
from urllib.parse import parse_qs
from abc import ABCMeta, abstractmethod

class ICapabilitiesDocument:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_service_title(self): raise NotImplementedError
    def get_service_metadata_url(self): raise NotImplementedError


class BaseCapabilitiesDocument():
    url = None
    xml_string = None
    etree = None
    namespaces = {}

    def __init__(self, input_string, namespaces):
        if os.path.isfile(input_string):
            with open(input_string) as md_file:
                xml_string = md_file.read().encode("utf-8")
        else:
            xml_string = input_string
        self.namespaces = namespaces
        self.xml_string = xml_string
        self.etree = et.fromstring(xml_string)

    def get_all_xpath_values(self, xpath, etree=None):
        if etree is None:
            etree = self.etree
        result = etree.xpath(xpath, namespaces=self.namespaces)
        return [item.text for item in result]

    def get_single_xpath_value(self, xpath, etree=None):
        if etree is None:
            etree = self.etree
        result = etree.xpath(xpath, namespaces=self.namespaces)
        if result:
            return result[0].text
        return None

    def get_all_xpath_atts(self, xpath, etree=None):
        if etree is None:
            etree = self.etree
        result = etree.xpath(xpath, namespaces=self.namespaces)
        return [item for item in result]

    def get_single_xpath_att(self, xpath, etree=None):
        if etree is None:
            etree = self.etree
        result = etree.xpath(xpath, namespaces=self.namespaces)
        if result:
            return result[0]
        return None

class WFSCapabilitiesDocument(BaseCapabilitiesDocument, ICapabilitiesDocument):
    def __init__(self, input_string):
        namespaces = {
            "gml": "http://www.opengis.net/gml/3.2",
            "wfs": "http://www.opengis.net/wfs/2.0",
            "ows": "http://www.opengis.net/ows/1.1",
            "xlink": "http://www.w3.org/1999/xlink",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "fes": "http://www.opengis.net/fes/2.0",
            "natura2000": "http://natura2000.geonovum.nl",
            "inspire_common": "http://inspire.ec.europa.eu/schemas/common/1.0",
            "inspire_dls": "http://inspire.ec.europa.eu/schemas/inspire_dls/1.0",
            "wfs": "http://www.opengis.net/wfs/2.0"
        }
        super(WFSCapabilitiesDocument, self).__init__(input_string, namespaces)

    def get_service_title(self):
        xpath = f"/wfs:WFS_Capabilities/ows:ServiceIdentification/ows:Title"
        title = self.get_single_xpath_value(xpath)
        return title
    
    def get_service_metadata_url(self):
        xpath = f"/wfs:WFS_Capabilities/ows:OperationsMetadata/ows:ExtendedCapabilities/inspire_dls:ExtendedCapabilities/inspire_common:MetadataUrl/inspire_common:URL"
        url = self.get_single_xpath_value(xpath)
        return url
    
    def convert_to_dictionary(self):
        result = {}
        result["service_title"] = self.get_service_title()
        result["service_metadata_url"] = self.get_service_metadata_url()
        return result

class WMSCapabilitiesDocument(BaseCapabilitiesDocument, ICapabilitiesDocument):
    def __init__(self, input_string):
        namespaces = {
            "wms": "http://www.opengis.net/wms", 
            "sld": "http://www.opengis.net/sld",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "ms": "http://mapserver.gis.umn.edu/mapserver", 
            "xlink": "http://www.w3.org/1999/xlink",
            "inspire_common": "http://inspire.ec.europa.eu/schemas/common/1.0", 
            "inspire_vs": "http://inspire.ec.europa.eu/schemas/inspire_vs/1.0", 
        }
        super(WMSCapabilitiesDocument, self).__init__(input_string, namespaces)

    def get_service_metadata_url(self):
        xpath = f"/wms:WMS_Capabilities/wms:Capability/inspire_vs:ExtendedCapabilities/inspire_common:MetadataUrl/inspire_common:URL"
        url = self.get_single_xpath_value(xpath)
        if url:
            return url
        return ""

    def get_service_title(self):
        xpath = f"/wms:WMS_Capabilities/wms:Service/wms:Title"
        title = self.get_single_xpath_value(xpath)
        return title
    
    def get_service_abstract(self):
        xpath = f"/wms:WMS_Capabilities/wms:Service/wms:Abstract"
        abstract = self.get_single_xpath_value(xpath)
        return abstract
    
    def get_service_keywords(self):
        xpath = f"/wms:WMS_Capabilities/wms:Service/wms:KeywordList/wms:Keyword[not(@vocabulary)]"
        abstract = self.get_all_xpath_values(xpath)
        return abstract

    def get_bbox(self):
        xpath = f"/wms:WMS_Capabilities/wms:Capability/wms:Layer/wms:EX_GeographicBoundingBox"
        result = {}
        xpath_west = f"{xpath}/wms:westBoundLongitude"
        xpath_east = f"{xpath}/wms:eastBoundLongitude"
        xpath_north = f"{xpath}/wms:northBoundLatitude"
        xpath_south = f"{xpath}/wms:southBoundLatitude"
        result["minx"] = self.get_single_xpath_value(xpath_west)
        result["maxx"] = self.get_single_xpath_value(xpath_east)
        result["maxy"] = self.get_single_xpath_value(xpath_north)
        result["miny"] = self.get_single_xpath_value(xpath_south)
        return result

    def get_ds_md_identifier(self, ds_metadata_url):
        parsed = urlparse.urlparse(ds_metadata_url)
        if not 'id' in parse_qs(parsed.query):
            return parse_qs(parsed.query)['uuid'][0]
        return parse_qs(parsed.query)['id'][0]
   
    def get_linked_md_records_identifiers(self):
        xpath = f"/wms:WMS_Capabilities/wms:Capability/wms:Layer/wms:Layer/wms:MetadataURL/wms:OnlineResource/@xlink:href"
        dataset_md_urls = self.get_all_xpath_atts(xpath)
        result = []
        for url in dataset_md_urls:
            ds_md_identifier = self.get_ds_md_identifier(url)
            ds_result = {}
            ds_result["dataset_md_identifier"] = ds_md_identifier
            result.append(ds_result)
        return result

    def convert_to_dictionary(self):
        result = {}
        result["service_title"] = self.get_service_title()
        result["service_abstract"] = self.get_service_abstract()
        result["keywords"] = self.get_service_keywords()
        result["bbox"] = self.get_bbox()
        result["linked_datasets"] = self.get_linked_md_records_identifiers()
        result["service_capabilities_url_wms"] = self.url
        result["service_metadata_url"] = self.get_service_metadata_url()
        return result
