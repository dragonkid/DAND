# !/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

"""
{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=+\\/&<>;\'"?%#$@. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def shape_children(children):
    shaped_children = {
        'address': {}
    }
    for child in children:
        if child.tag == 'tag':
            k = child.attrib['k']
            if re.search(problemchars, k):
                continue
            v = child.attrib['v']
            splited_k = k.split(':')
            if len(splited_k) > 2:
                continue
            elif len(splited_k) == 2:
                prefix, real_k = splited_k
                if prefix != 'addr':
                    print('unexpected prefix {}'.format(prefix))
                    continue
                shaped_children['address'][real_k] = v
            else:
                shaped_children[splited_k[0]] = v
        elif child.tag == 'nd':
            shaped_children.setdefault('node_refs', []).append(child.attrib['ref'])
        else:
            print('warning: unknown tag {}'.format(child))
    if not shaped_children['address']:
        del shaped_children['address']

    return shaped_children


def shape_element(element):
    shaped_element = {
        'created': {}
    }
    if element.tag not in ['node', 'way']:
        return

    node_attrs = element.attrib

    if 'lat' in node_attrs and 'lon' in node_attrs:
        shaped_element['pos'] = [float(node_attrs['lat']), float(node_attrs['lon'])]
    shaped_element['id'] = node_attrs['id']
    shaped_element['visible'] = node_attrs.get('visible', 'true')
    shaped_element['type'] = element.tag
    shaped_element['created'] = {
        'changeset': node_attrs['changeset'],
        'user': node_attrs['user'],
        'version': node_attrs['version'],
        'uid': node_attrs['uid'],
        'timestamp': node_attrs['timestamp'],
    }
    shaped_element.update(shape_children(element.getchildren()))

    return shaped_element


def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            shaped_element = shape_element(element)
            if shaped_element:
                data.append(shaped_element)
                if pretty:
                    fo.write(json.dumps(shaped_element, indent=2) + "\n")
                else:
                    fo.write(json.dumps(shaped_element) + "\n")
    return data


def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    # pprint.pprint(data)

    correct_first_elem = {
        "id": "261114295",
        "visible": "true",
        "type": "node",
        "pos": [41.9730791, -87.6866303],
        "created": {
            "changeset": "11129782",
            "user": "bbmiller",
            "version": "7",
            "uid": "451048",
            "timestamp": "2012-03-28T18:31:23Z"
        },
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
        "street": "West Lexington St.",
        "housenumber": "1412"
    }
    assert data[-1]["node_refs"] == ["2199822281", "2199822390", "2199822392", "2199822369",
                                     "2199822370", "2199822284", "2199822281"]


if __name__ == "__main__":
    import ipdb, traceback, sys
    try:
        test()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)

