import click
import pytest
from shapely.geometry import CAP_STYLE
from shapely.geometry import JOIN_STYLE

import fio_buffer.core


def test_cb_cap_style():
    cap_styles = {a: getattr(CAP_STYLE, a) for a in dir(CAP_STYLE) if not a.startswith('_')}
    for style, val in cap_styles.items():
        assert fio_buffer.core._cb_cap_style(None, None, style) == val


def test_cb_join_style():
    join_styles = {a: getattr(JOIN_STYLE, a) for a in dir(JOIN_STYLE) if not a.startswith('_')}
    for style, val in join_styles.items():
        assert fio_buffer.core._cb_join_style(None, None, style) == val

def test_cb_res():
    assert fio_buffer.core._cb_res(None, None, 1) == 1
    assert fio_buffer.core._cb_res(None, None, 0) == 0
    with pytest.raises(click.BadParameter):
        assert fio_buffer.core._cb_res(None, None, -1)
