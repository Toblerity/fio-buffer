==========
fio-buffer
==========

.. image:: https://travis-ci.org/geowurster/fio-buffer.svg?branch=master
    :target: https://travis-ci.org/geowurster/fio-buffer?branch=master

.. image:: https://coveralls.io/repos/geowurster/fio-buffer/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/fio-buffer?branch=master

A `Fiona <http://toblerity.org/fiona/manual.html>`_  CLI plugin for buffering geometries.  Powered by `buffer <http://toblerity.org/shapely/manual.html#object.buffer>`_.

Buffering geometries is an embarrassingly parallel task that benefits greatly from
parallelization.  Large complex geometries with a large number of vertexes take much longer
to process than simple small ones.  Use the ``--jobs`` flag to spread processing across a
number of cores but remember that the output feature order is not guaranteed to be the same
as the input feature order.


Usage
=====

.. code-block:: console

    Usage: fio buffer [OPTIONS] INFILE OUTFILE

      Geometries can be dilated with a positive distance, eroded with a negative
      distance, and in some cases cleaned or repaired with a distance of 0.

      Examples
      --------

      Default settings - buffer geometries in the input CRS:

          $ fio buffer in.geojson out.geojson --dist 10

      Dynamically buffer geometries by a distance stored in the field
      `magnitude` and write as GeoJSON:

          $ fio buffer \
              in.shp \
              out.geojson \
              --driver GeoJSON \
              --dist magnitude

      Read geometries from one CRS, buffer in another, and then write to a
      third:

          $ fio buffer in.shp out.shp \
              --dist 10 \
              --buf-crs EPSG:3857 \
              --dst-crs EPSG:32618

      Control cap style, mitre limit, segment resolution, and join style:

          $ fio buffer in.geojson out.geojson \
              --dist 0.1 \
              --res 5 \
              --cap-style flat \
              --join-style mitre \
              --mitre-limit 0.1\

    Options:
      -f, --format, --driver NAME     Output driver name.  [required]
      --cap-style [flat|round|square]
                                      Where geometries terminate, use this style.
                                      (default: round)
      --join-style [round|mitre|bevel]
                                      Where geometries touch, use this style.
                                      (default: round)
      --res INTEGER                   Resolution of the buffer around each vertex
                                      of the object. (default: 16)
      --mitre-limit FLOAT             When using a mitre join, limit the maximum
                                      length of the join corner according to this
                                      ratio. (default: 0.5)
      --dist FLOAT | FIELD            Buffer distance in georeferenced units
                                      according to --buf-dist.  [required]
      --src-crs TEXT                  Specify CRS for input data.  Not needed if
                                      set in input file.
      --buf-crs TEXT                  Perform buffer operations in a different
                                      CRS. (default: --src-crs)
      --dst-crs TEXT                  Reproject geometries to a different CRS
                                      before writing.  Must be combined with
                                      --buf-crs. (default: --src-crs)
      --otype GEOMTYPE                Specify output geometry type. (default:
                                      MultiPolygon)
      --skip-failures                 Skip geometries that fail somewhere in the
                                      processing pipeline.
      --jobs CORES                    Process geometries in parallel across N
                                      cores.  The goal of this flag is speed so
                                      feature order and ID's are not preserved.
                                      (default: 1)
      --help                          Show this message and exit.


Installing
==========

Via pip:

.. code-block:: console

    $ pip install fio-buffer

From source:

.. code-block:: console

    $ git clone https://github.com/geowurster/fio-buffer
    $ cd fio-buffer
    $ python setup.py install


Developing
==========

.. code-block:: console

    $ git clone https://github.com/geowurster/fio-buffer
    $ cd fio-buffer
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .[test]
    $ py.test tests --cov fio_buffer --cov-report term-missing


License
=======

See ``LICENSE.txt``.
