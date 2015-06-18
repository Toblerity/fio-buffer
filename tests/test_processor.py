from fiona.transform import transform_geom
from shapely.geometry import mapping
from shapely.geometry import shape

import fio_buffer.core


feature = {
    'type': 'Feature',
    'properties': {'prop1': 1, 'prop2': None},
    'geometry': {
        'type': 'Polygon',
        'coordinates': [[[-1, -1], [-1, 1], [1, 1], [1, -1]]]
    }
}


def round7(val):
    return round(val, 7)


def test_just_buffer():
    args = {
        'feat': feature,
        'src_crs': None,
        'buf_crs': None,
        'dst_crs': None,
        'skip_failures': False,
        'buf_args': {'distance': 10},
    }
    expected = {
        'type': 'Feature',
        'properties': feature['properties'],
        'geometry': mapping(shape(feature['geometry']).buffer(**args['buf_args']))
    }
    actual = fio_buffer.core._processor(args)

    assert expected.keys() == actual.keys()
    assert expected['properties'] == actual['properties']

    for a_pair, e_pair in zip(
            expected['geometry']['coordinates'][0], actual['geometry']['coordinates'][0]):
        assert list(map(round7, a_pair)) == list(map(round7, e_pair))
