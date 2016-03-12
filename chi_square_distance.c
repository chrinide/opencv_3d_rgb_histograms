/*
 * Code modified from Craig Ringer's excellent answer to this
 * post: http://stackoverflow.com/questions/16992339/
 *
 * Copyright (C) 2016, Christopher Swingley
 * <cswingle@swingleydev.com>
 */

#include <postgres.h>
#include <fmgr.h>
#include <utils/array.h>
#include <utils/lsyscache.h>

/* From intarray contrib header */
#define ARRPTR(x) ( (float8 *) ARR_DATA_PTR(x) )

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(chi_square_distance);
Datum chi_square_distance(PG_FUNCTION_ARGS);

/*
 * Returns the chi squared distance between two double precision arrays.
 */
Datum chi_square_distance(PG_FUNCTION_ARGS) {
    ArrayType *a, *b;
    float8 *da, *db;

    float8 sum = 0.0;
    int i, n;

    if (PG_ARGISNULL(0)) {
        ereport(ERROR, (errmsg("First operand must be non-null")));
    }
    a = PG_GETARG_ARRAYTYPE_P(0);

    if (PG_ARGISNULL(1)) {
        ereport(ERROR, (errmsg("Second operand must be non-null")));
    }
    b = PG_GETARG_ARRAYTYPE_P(1);

    if (ARR_NDIM(a) != 1 || ARR_NDIM(b) != 1) {
        ereport(ERROR, (errmsg("One-dimensional arrays are required")));
    }

    n = (ARR_DIMS(a))[0];
    if (n != (ARR_DIMS(b))[0]) {
        ereport(ERROR, (errmsg("Arrays are of different lengths")));
    }

    da = ARRPTR(a);
    db = ARRPTR(b);

    // Generate the sums.
    for (i = 0; i < n; i++) {
        if (*da - *db) {
            sum = sum + ((*da - *db) * (*da - *db) / (*da + *db));
        }
        da++;
        db++;
    }

    sum = sum / 2.0;

    PG_RETURN_FLOAT8(sum);
}
