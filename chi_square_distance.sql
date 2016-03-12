CREATE OR REPLACE FUNCTION chi_square_distance(a numeric[], b numeric[])
RETURNS numeric AS $_$
    DECLARE
        sum numeric := 0.0;
        i integer;
    BEGIN
        IF array_upper(a, 1) <> array_upper(b, 1) THEN
            RAISE EXCEPTION 'histogram lengths not identical.';
            RETURN NULL;
        END IF;

        FOR i IN 1 .. array_upper(a, 1)
        LOOP
            IF a[i]+b[i] > 0 THEN
                sum = sum + (a[i]-b[i])^2 / (a[i]+b[i]);
            END IF;
        END LOOP;

        RETURN sum/2.0;
    END;
$_$
LANGUAGE plpgsql;
