==========
fio-buffer
==========

.. image:: https://travis-ci.org/geowurster/fio-buffer.svg?branch=master
    :target: https://travis-ci.org/geowurster/fio-buffer?branch=master

.. image:: https://coveralls.io/repos/geowurster/fio-buffer/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/fio-buffer?branch=master

A `Fiona <http://toblerity.org/fiona/manual.html>`_  CLI plugin for buffering geometries.  Powered by `shapely <http://toblerity.org/shapely/manual.html>`_.


Usage
=====

.. code-block:: console

    Usage: fio buffer [OPTIONS] INFILE OUTFILE

      Buffer geometries with shapely.

      Default settings - buffer geometries in the input CRS:

          $ fio buffer ${INFILE} ${OUTFILE} --dist 10

      Read geometries from one CRS, buffer in another, and then write to a
      third:

          $ fio buffer ${INFILE} ${OUTFILE} \
              --dist 10 \
              --buf-crs EPSG:3857 \
              --dst-crs EPSG:32618

      Control cap style, mitre limit, segment resolution, and join style:

          $ fio buffer ${INFILE} ${OUTFILE} \
              --dist 0.1 \
              --res 5 \
              --cap-style flat \
              --join-style mitre \
              --mitre-limit 0.1\

    Options:
      -f, --format, --driver NAME     Output driver name. (default: infile's
                                      driver)
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
      --dist FLOAT                    Buffer distance in georeferenced units.  If
                                      `--buf-crs` is supplied, then units must
                                      match that CRS.  [required]
      --src-crs TEXT                  Specify CRS for input data.  Not needed if
                                      specified in infile.
      --buf-crs TEXT                  Perform buffer operations in a different
                                      CRS.  Defaults to `--src-crs` if not
                                      specified.
      --dst-crs TEXT                  Reproject geometries to a different CRS
                                      before writing.  Defaults to `--src-crs` if
                                      not specified.
      --otype GEOMTYPE                Specify output geometry type. (default:
                                      MultiPolygon)
      --skip-failures                 Skip geometries that fail somewhere in the
                                      processing pipeline.
      --jobs CORES                    Process geometries in parallel across N
                                      cores.  The goal of this flag is speed so
                                      feature order is not preserved. (default: 1)
      --help                          Show this message and exit.


Examples
========

In order to just buffer geometries in their native CRS, use the following command:

.. code-block:: console

    $ fio buffer --dist 10 ${INFILE} ${OUTFILE}

The additional ``--buf-crs`` and ``--dst-crs`` options can be used to read geometries
in one CRS, buffer in another, and reproject before writing to a third.  ``--src-crs``
is provided for input files with an unset CRS definition.

.. code-block:: console

    $ fio buffer \
        --dist 1200 \
        ${INFILE ${OUTFILE} \
        --buf-crs EPSG:32618 \
        --dst-crs EPSG:4326

Shapely's `buffer <http://toblerity.org/shapely/manual.html#object.buffer>`_ method is used and
has some additional arguments that are available through ``--cap-style``, ``--join-style``, etc.

Buffering geometries is an embarrassingly parallel task that benefits greatly from
parallelization.  Large complex geometries with a large number of vertexes take much longer
to process than simple small ones.  Use the ``--jobs`` flag to spread processing across a
number of cores but remember that the output feature order is not guaranteed to be the same
as the input feature order.


Installing
==========

Dependencies
------------

The primary dependencies are `Fiona <https://github.com/Toblerity/Fiona#installation>`_ and `Shapely <https://github.com/toblerity/shapely#installing-shapely>`_,
which can be installed via ``pip`` on most systems and will be automatically installed when
installing ``fio-buffer``.

Via pip:

.. code-block:: console

    $ pip install fio-buffer

From source:

.. code-block:: console

    $ git clone https://github.com/geowurster/fio-buffer
    $ cd fio-buffer
    $ python setup.py install


Developing
----------

.. code-block:: console

    $ git clone https://github.com/geowurster/fio-buffer
    $ cd fio-buffer
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -e .[test]
    $ py.test tests --cov fio_buffer --cov-report term-missing

License
-------

See ``LICENSE.txt``.
