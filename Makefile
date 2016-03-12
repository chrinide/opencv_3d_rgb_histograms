MODULES = chi_square_distance

PG_CONFIG = pg_config

PGXS = $(shell $(PG_CONFIG) --pgxs)
INCLUDEDIR = $(shell $(PG_CONFIG) --includedir-server)
include $(PGXS)

chi_square_distance.so: chi_square_distance.o
	cc -shared -o chi_square_distance.so chi_square_distance.o

chi_square_distance.o: chi_square_distance.c
	cc -o chi_square_distance.o -c chi_square_distance.c $(CFLAGS) -I$(INCLUDEDIR)

# make
# copy chi_square_distance.so to $(pg_config --pkglibdir)
#
# CREATE FUNCTION chi_square_distance(a double precision[], b double precision[])
# RETURNS double precision
# AS 'chi_square_distance', 'chi_square_distance'
# LANGUAGE C STRICT;
