

"""
Core components for fio-buffer
"""


import copy
import logging
from multiprocessing import cpu_count, Pool

import click
import fiona as fio
from fiona.transform import transform_geom
from shapely.geometry import CAP_STYLE
from shapely.geometry import JOIN_STYLE
from shapely.geometry import mapping
from shapely.geometry import shape

from . import __version__


logging.basicConfig()
logger = logging.getLogger('fio-buffer')


def _cb_cap_style(ctx, param, value):

    """
    Click callback to transform `--cap-style` to an `int`.
    """

    return getattr(CAP_STYLE, value)


def _cb_join_style(ctx, param, value):

    """
    Click callback to transform `--join-style` to an `int`.
    """

    return getattr(JOIN_STYLE, value)


def _cb_res(ctx, param, value):

    """
    Click callback to ensure `--res` is `>= 0`.
    """

    if value < 0:
        raise click.BadParameter("must be a positive value")

    return value


def _cb_dist(ctx, param, value):

    """
    Click callback to ensure `--distance` can be either a float or a field name.
    """

    try:
        return float(value)
    except ValueError:
        return value


def _processor(args):

    """
    Process a single feature.

    Parameters
    ----------
    args : dict
        feat : dict
            A GeoJSON feature to process.
        src_crs : str or dict
            The geometry's CRS.
        buf_crs : str or dict
            Apply buffer after reprojecting to this CRS.
        dst_crs : str or dict
            Reproject buffered geometry to this CRS before returning.
        skip_failures : bool
            If True then Exceptions don't stop processing.
        buf_args : dict
            Keyword arguments for the buffer operation.

    Returns
    -------
    dict
        GeoJSON feature with updated geometry.
    """

    feat = args['feat']
    src_crs = args['src_crs']
    buf_crs = args['buf_crs']
    dst_crs = args['dst_crs']
    skip_failures = args['skip_failures']
    buf_args = args['buf_args']

    # Support buffering by a field's value
    if not isinstance(buf_args['distance'], (float, int)):
        field_val = feat['properties'][buf_args['distance']]

        # Buffering according to a field but field is None so just return the feature
        if field_val is None:
            return feat
        else:
            buf_args['distance'] = field_val

    try:
        # src_crs -> buf_crs
        reprojected = transform_geom(
            src_crs, buf_crs, feat['geometry'],
            antimeridian_cutting=True
        )

        # buffering operation
        buffered = shape(reprojected).buffer(**buf_args)

        # buf_crs -> dst_crs
        feat['geometry'] = transform_geom(
            buf_crs, dst_crs, mapping(buffered),
            antimeridian_cutting=True
        )

        return feat

    except Exception:
        logger.exception("Feature with ID %s failed during buffering", feat.get('id'))
        if not skip_failures:
            raise


@click.command(short_help="Buffer geometries on all sides by a fixed distance.")
@click.version_option(prog_name='fio-buffer', version=__version__)
@click.argument('infile', required=True)
@click.argument('outfile', required=True)
@click.option(
    '-f', '--format', '--driver', metavar='NAME',
    help="Output driver name.  Derived from the input datasource if not given."
)
@click.option(
    '--cap-style', type=click.Choice(['flat', 'round', 'square']),
    default='round', show_default=True,
    callback=_cb_cap_style, help="Where geometries terminate, use this style."
)
@click.option(
    '--join-style', type=click.Choice(['round', 'mitre', 'bevel']),
    default='round', show_default=True,
    callback=_cb_join_style, help="Where geometries touch, use this style."
)
@click.option(
    '--res', type=click.INT, callback=_cb_res, default=16, show_default=True,
    help="Resolution of the buffer around each vertex of the geometry."
)
@click.option(
    '--mitre-limit', type=click.FLOAT, default=5.0, show_default=True,
    help="When using a mitre join, limit the maximum length of the join corner according to "
         "this ratio."
)
@click.option(
    '--distance', metavar='FLOAT|FIELD', required=True, callback=_cb_dist,
    help="Buffer distance or field containing distance values.  Units match --buf-crs.  "
         "When buffering with a field, feature's with a null value are unaltered."
)
@click.option(
    '--src-crs', help="Specify CRS for input data.  Not needed if set in input file."
)
@click.option(
    '--buf-crs', help="Perform buffer operations in a different CRS. [default: --src-crs]"
)
@click.option(
    '--dst-crs', help="Reproject geometries to a different CRS before writing.  Must be "
                      "combined with --buf-crs. [default: --src-crs]"
)
@click.option(
    '--geom-type', 'output_geom_type', default='MultiPolygon',
    metavar='GEOMTYPE', show_default=True,
    help="Output layer's geometry type."
)
@click.option(
    '--skip-failures', is_flag=True,
    help="Skip geometries that fail somewhere in the processing pipeline."
)
@click.option(
    '--jobs', type=click.IntRange(1, cpu_count()), default=1,
    metavar="CORES", show_default=True,
    help="Process geometries in parallel across N cores.  Feature ID's and order are not "
         "preserved if more that 1 cores are used."
)
@click.pass_context
def buffer(ctx, infile, outfile, driver, cap_style, join_style, res, mitre_limit,
           distance, src_crs, buf_crs, dst_crs, output_geom_type, skip_failures, jobs):

    """
    Geometries can be dilated with a positive distance, eroded with a negative
    distance, and in some cases cleaned or repaired with a distance of 0.

    \b
    Examples
    --------

    Default settings - buffer geometries in the input CRS:

    \b
        $ fio buffer in.geojson out.geojson --distance 10

    Dynamically buffer geometries by a distance stored in the field 'magnitude'
    and write as GeoJSON:

    \b
        $ fio buffer \\
            in.shp \\
            out.geojson \\
            --driver GeoJSON \\
            --distance magnitude

    Read geometries from one CRS, buffer in another, and then write to a third:

    \b
        $ fio buffer in.shp out.shp \\
            --distance 10 \\
            --buf-crs EPSG:3857 \\
            --dst-crs EPSG:32618

    Control cap style, mitre limit, segment resolution, and join style:

    \b
        $ fio buffer in.geojson out.geojson \\
            --distance 0.1 \\
            --res 5 \\
            --cap-style flat \\
            --join-style mitre \\
            --mitre-limit 0.1\\
    """

    if dst_crs and not buf_crs:
        raise click.ClickException("Must specify --buf-crs when using --dst-crs.")

    # fio has a -v flag so just use that to set the logging level
    # Extra checks are so this plugin doesn't just completely crash due
    # to upstream changes.
    if isinstance(getattr(ctx, 'obj'), dict):
        logger.setLevel(ctx.obj.get('verbosity', 1))

    with fio.open(infile) as src:

        logger.debug("Resolving CRS fall backs")

        src_crs = src_crs or src.crs
        buf_crs = buf_crs or src_crs
        dst_crs = dst_crs or src_crs

        if not src_crs:
            raise click.ClickException(
                "CRS is not set in input file.  Use --src-crs to specify.")

        logger.debug("src_crs=%s", src_crs)
        logger.debug("buf_crs=%s", buf_crs)
        logger.debug("dst_crs=%s", dst_crs)

        meta = copy.deepcopy(src.meta)
        meta.update(
            driver=driver or src.driver,
            crs=dst_crs
        )
        if output_geom_type:
            meta['schema'].update(geometry=output_geom_type)

        logger.debug("Creating output file %s", outfile)
        logger.debug("Meta=%s", meta)

        with fio.open(outfile, 'w', **meta) as dst:

            # Keyword arguments for `<Geometry>.buffer()`
            buf_args = {
                'distance': distance,
                'resolution': res,
                'cap_style': cap_style,
                'join_style': join_style,
                'mitre_limit': mitre_limit
            }

            # A generator that produces the arguments required for `_processor()`
            task_generator = (
                {
                    'feat': feat,
                    'src_crs': src_crs,
                    'buf_crs': buf_crs,
                    'dst_crs': dst_crs,
                    'skip_failures': skip_failures,
                    'buf_args': buf_args
                } for feat in src)

            logger.debug("Starting processing on %s cores", jobs)
            for o_feat in Pool(jobs).imap_unordered(_processor, task_generator):
                if o_feat is not None:
                    try:
                        dst.write(o_feat)
                    except Exception:
                        logger.exception(
                            "Feature with ID %s failed during write", o_feat.get('id'))
                        if not skip_failures:
                            raise

            logger.debug("Finished processing.")
