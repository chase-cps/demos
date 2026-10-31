/* The climb rate of the drone of DroneAltitude, limited to vmax = 3 up or
   down: its contract in ACSL, the language of Frama-C. */

/*@ requires -100 <= v <= 100;
    ensures -3 <= \result <= 3;
    ensures (-3 <= v <= 3) ==> \result == v;
*/
int limit(int v)
{
    if (v > 3)
        return 3;
    if (v < -3)
        return -3;
    return v;
}

/* The same limit with the test of the top written v > 4: a rate of 4 goes
   through. */
/*@ requires -100 <= v <= 100;
    ensures -3 <= \result <= 3;
    ensures (-3 <= v <= 3) ==> \result == v;
*/
int limit_loose(int v)
{
    if (v > 4)
        return 3;
    if (v < -3)
        return -3;
    return v;
}
