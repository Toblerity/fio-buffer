from click.testing import CliRunner
import fiona as fio
from fiona.transform import transform_geom

from shapely.geometry import mapping
from shapely.geometry import shape

import fio_buffer.core


def test_standard(tmpdir):
    outfile = str(tmpdir.mkdir('out').join("buf-1.geojson"))
    result = CliRunner().invoke(fio_buffer.core.buffer, [
        'tests/data/points.geojson',
        outfile,
        '--dist', '1',
        '--driver', 'GeoJSON'
    ])
    assert result.exit_code == 0
    with fio.open('tests/data/points.geojson') as points, fio.open(outfile) as actual:
        for pnt, buf in zip(points, actual):
            e_coords = mapping(shape(pnt['geometry']).buffer(1))['coordinates'][0]
            a_coords = buf['geometry']['coordinates'][0]
            for e_pair, a_pair in zip(e_coords, a_coords):

                # Multipolygons can creep in and mess up the test so just skip them
                if buf['geometry']['type'] == 'Polygon':
                    e_x, e_y = e_pair
                    a_x, a_y = a_pair
                    assert round(e_x, 7) == round(a_x, 7)
                    assert round(e_y, 7) == round(a_y, 7)


def test_distance_field(tmpdir):
    outfile = str(tmpdir.mkdir('out').join("buf-field.geojson"))
    result = CliRunner().invoke(fio_buffer.core.buffer, [
        'tests/data/points.geojson',
        outfile,
        '--dist', 'distance',
        '--driver', 'GeoJSON'
    ])
    assert result.exit_code == 0
    with fio.open('tests/data/points.geojson') as points, fio.open(outfile) as actual:
        for pnt, buf in zip(points, actual):
            dist = buf['properties']['distance']
            e_coords = mapping(shape(pnt['geometry']).buffer(dist))['coordinates'][0]
            a_coords = buf['geometry']['coordinates'][0]
            for e_pair, a_pair in zip(e_coords, a_coords):
                # Multipolygons can creep in and mess up the test so just skip them
                if buf['geometry']['type'] == 'Polygon':
                    e_x, e_y = e_pair
                    a_x, a_y = a_pair
                    assert round(e_x, 7) == round(a_x, 7)
                    assert round(e_y, 7) == round(a_y, 7)


def test_buf_crs(tmpdir):
    outfile = str(tmpdir.mkdir('out').join("buf-field.geojson"))
    result = CliRunner().invoke(fio_buffer.core.buffer, [
        'tests/data/points.geojson',
        outfile,
        '--dist', '100',
        '--driver', 'GeoJSON',
        '--buf-crs', 'EPSG:3857'
    ])
    assert result.exit_code == 0
    with fio.open('tests/data/points.geojson') as points, fio.open(outfile) as actual:
        for pnt, buf in zip(points, actual):

            # Reproject, buffer, reroject to create an expected geometry
            geom = transform_geom('EPSG:4326', 'EPSG:3857', pnt['geometry'])
            buf_geom = mapping(shape(geom).buffer(100))
            e_coords = transform_geom('EPSG:3857', 'EPSG:4326', buf_geom)['coordinates'][0]

            a_coords = buf['geometry']['coordinates'][0]
            for e_pair, a_pair in zip(e_coords, a_coords):
                # Multipolygons can creep in and mess up the test so just skip them
                if buf['geometry']['type'] == 'Polygon':
                    e_x, e_y = e_pair
                    a_x, a_y = a_pair
                    assert round(e_x, 7) == round(a_x, 7)
                    assert round(e_y, 7) == round(a_y, 7)


def test_buf_dst_crs(tmpdir):
    outfile = str(tmpdir.mkdir('out').join("buf-field.geojson"))
    result = CliRunner().invoke(fio_buffer.core.buffer, [
        'tests/data/points.geojson',
        outfile,
        '--dist', '100',
        '--driver', 'GeoJSON',
        '--buf-crs', 'EPSG:3857',
        '--dst-crs', 'EPSG:900913'
    ])
    assert result.exit_code == 0
    with fio.open('tests/data/points.geojson') as points, fio.open(outfile) as actual:
        for pnt, buf in zip(points, actual):

            # Reproject, buffer, reroject to create an expected geometry
            geom = transform_geom('EPSG:4326', 'EPSG:3857', pnt['geometry'])
            buf_geom = mapping(shape(geom).buffer(100))
            e_coords = transform_geom('EPSG:3857', 'EPSG:900913', buf_geom)['coordinates'][0]

            a_coords = buf['geometry']['coordinates'][0]
            for e_pair, a_pair in zip(e_coords, a_coords):
                # Multipolygons can creep in and mess up the test so just skip them
                if buf['geometry']['type'] == 'Polygon':
                    e_x, e_y = e_pair
                    a_x, a_y = a_pair
                    assert round(e_x, 7) == round(a_x, 7)
                    assert round(e_y, 7) == round(a_y, 7)
