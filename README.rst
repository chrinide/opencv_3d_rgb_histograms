RGB Histogram
=============

The idea is to generate a 3-D RGB histogram (bins for R and G and B
combinations) for a series of images so we can order them by similarity
or search for images most similar to an existing image.

The code basically comes from:

http://www.pyimagesearch.com/2014/01/27/hobbits-and-histograms-a-how-to-guide-to-building-your-first-image-search-engine-in-python/

Files:

* ``chi_square_distance.sql``: A SQL function to calculate the chi
  square distance between to histogram arrays.

* ``chi_square_distance.c``: C version of the chi square distance
  calculation.

* ``Makefile``: Makefile for the C shared library.  After building:

.. code:: bash

   $ sudo cp chi_square_distance.so $(pg_config --pkglibdir)

.. code:: sql

   CREATE FUNCTION chi_square_distance(a double precision[], b double precision[])
   RETURNS double precision
   AS 'chi_square_distance', 'chi_square_distance'
   LANGUAGE C STRICT;

* ``generate_photolog_histograms.py``: A Python script to populate the
  photolog_histograms table.

* ``rgb_histogram.py``: A Python script that builds a CSV of 3D RGB
  histogram distances for all photos in a directory.

Updating distances:

.. code:: sql

   INSERT INTO photolog_histogram_distances
   (a_id, b_id, bins, distance)
   (SELECT a.id, b.id, 32,
      chi_square_distance(a.rgb_histogram, b.rgb_histogram)
    FROM photolog_histograms AS a
      INNER JOIN photolog_histograms AS b
         ON a.id < b.id AND a.bins = b.bins
    WHERE a.bins = 32 AND a.id || '-' || b.id NOT IN
    (SELECT a.id || '-' || b.id FROM photolog_histograms
     WHERE bins = 32));

Notes:

* generate_photolog_histograms.py took 45 minutes with 32 bins.

* rgb_histogram.py took a little over 29 minutes to do every pairwise
  distance twice (1-2 and 2-1) with 8 bins.

* chi_square_distance.sql took just under two hours to do every pairwise
  distance once with 8 bins.

* chi_square_distance.c took 79 *seconds* using 8 bin histograms and 450
  seconds using 16 bit histograms.  32 bin histogram distances took 54
  minutes to compute.

.. vim:ft=rst:fenc=utf-8:tw=72:ts=3:sw=3:sts=3

