import re
from typing import List


def custom_xml_parser(xml_string: str, tags: List[str]) -> List[str]:
    # Parse the XML string
    output = {}
    for tag in tags:
        pattern = rf"<{tag}>(.*?)</{tag}>"
        # Extract the text from the tags
        output[tag] = re.search(pattern, xml_string, re.DOTALL).group(1).strip()
    return output
