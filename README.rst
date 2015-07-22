==========
fio-buffer
==========

.. image:: https://travis-ci.org/geowurster/fio-buffer.svg?branch=master
    :target: https://travis-ci.org/geowurster/fio-buffer?branch=master

.. image:: https://coveralls.io/repos/geowurster/fio-buffer/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/fio-buffer?branch=master

A `Fiona <http://toblerity.org/fiona/manual.html>`_  CLI plugin for buffering geometries in parallel.  Powered by `Shapely <http://toblerity.org/shapely/manual.html#object.buffer>`_.


Usage
=====

.. code-block:: console

    Usage: fio buffer [OPTIONS] INFILE OUTFILE

      Geometries can be dilated with a positive distance, eroded with a negative
      distance, and in some cases cleaned or repaired with a distance of 0.

      Examples
      --------

      Default settings - buffer geometries in the input CRS:

          $ fio buffer in.geojson out.geojson --distance 10

      Dynamically buffer geometries by a distance stored in the field
      'magnitude' and write as GeoJSON:

          $ fio buffer \
              in.shp \
              out.geojson \
              --driver GeoJSON \
              --distance magnitude

      Read geometries from one CRS, buffer in another, and then write to a
      third:

          $ fio buffer in.shp out.shp \
              --distance 10 \
              --buf-crs EPSG:3857 \
              --dst-crs EPSG:32618

      Control cap style, mitre limit, segment resolution, and join style:

          $ fio buffer in.geojson out.geojson \
              --distance 0.1 \
              --res 5 \
              --cap-style flat \
              --join-style mitre \
              --mitre-limit 0.1\

    Options:
      --version                       Show the version and exit.
      -f, --format, --driver NAME     Output driver name.  Derived from the input
                                      datasource if not given.
      --cap-style [flat|round|square]
                                      Where geometries terminate, use this style.
                                      [default: round]
      --join-style [round|mitre|bevel]
                                      Where geometries touch, use this style.
                                      [default: round]
      --res INTEGER                   Resolution of the buffer around each vertex
                                      of the geometry.  [default: 16]
      --mitre-limit FLOAT             When using a mitre join, limit the maximum
                                      length of the join corner according to this
                                      ratio.  [default: 5.0]
      --distance FLOAT|FIELD          Buffer distance or field containing distance
                                      values.  Units match --buf-crs.  When
                                      buffering with a field, feature's with a
                                      null value are unaltered.  [required]
      --src-crs TEXT                  Specify CRS for input data.  Not needed if
                                      set in input file.
      --buf-crs TEXT                  Perform buffer operations in a different
                                      CRS. [default: --src-crs]
      --dst-crs TEXT                  Reproject geometries to a different CRS
                                      before writing.  Must be combined with
                                      --buf-crs. [default: --src-crs]
      --geom-type GEOMTYPE            Output layer's geometry type.  [default:
                                      MultiPolygon]
      --skip-failures                 Skip geometries that fail somewhere in the
                                      processing pipeline.
      --jobs CORES                    Process geometries in parallel across N
                                      cores.  Feature ID's and order are not
                                      preserved if more that 1 cores are used.
                                      [default: 1]
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
    $ pip install -e .[dev]
    $ py.test tests --cov fio_buffer --cov-report term-missing


License
=======

See ``LICENSE.txt``.
