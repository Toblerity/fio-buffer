from click.testing import CliRunner

import fio_buffer.core


def test_dst_crs_no_buf_crs():
    result = CliRunner().invoke(fio_buffer.core.buffer, [
        'tests/data/points.geojson',
        'should-not-be-written',
        '--driver', 'GeoJSON',
        '--dist', '1',
        '--dst-crs', 'EPSG:3857'
    ])
    assert result.exit_code != 0
