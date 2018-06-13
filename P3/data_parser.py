# !/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json

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
            k, v = fix_kv(k, v)
            splited_k = k.split(':')
            if len(splited_k) > 2 or v == 'multipolygon':
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


def fix_kv(k, v):
    if k == type:
        if v in ['国槐', 'Cypress']:
            k = 'species'
        elif v in ['公园', '应急避难场所']:
            k = '应急避难场所类型'
        elif v == 'office':
            k = 'building'
        else:
            pass
    if k in ['疏散人数（万）', '疏散人数(万人)', '应急避难场所疏散人数万人', '应急避难场所疏散人口万人', '应急避难人数（万人）']:
        k = 'capacities'
        v = float(v)
    if k == '疏散人数':
        k = 'capacities'
        v = int(v.strip(' people').replace(',', '')) / 10000
    if k == 'phone':
        v = '+86-10-{}'.format(v[-8:])
    return k, v


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


if __name__ == "__main__":
    import ipdb, traceback, sys
    try:
        process_map('beijing_china.osm')
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)

