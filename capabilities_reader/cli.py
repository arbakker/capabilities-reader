import argparse
import json
import uuid
import requests
from .cap_document import WMSCapabilitiesDocument, WFSCapabilitiesDocument

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument('--service-type', dest='service_type')
    parser.add_argument('--mergejson', dest='mergejson')
    args = parser.parse_args()
    url = args.url
    resp = requests.get(url)
    xml_string = resp.text.encode('utf-8')
    service_type = args.service_type
    if service_type == "WMS":
        service_record = WMSCapabilitiesDocument(xml_string)
    elif service_type == "WFS":
        service_record = WFSCapabilitiesDocument(xml_string)
    else:
        raise ValueError(f"service-type {service_type} not supported")
    service_record.url = url
    result = service_record.convert_to_dictionary()
    if not "md_identifier" in result.keys():
        result["md_identifier"] = str(uuid.uuid1())
    print(json.dumps(result))


if __name__ == "__main__":
    main()
