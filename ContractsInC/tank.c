/* The pump of a water tank, one call: its contract in the clauses of
   ESBMC. Open the file with chase-cps view (or in VS Code): each function
   is a box, checked against its clauses. */

int pump(int level)
{
    __ESBMC_requires(level >= 0 && level <= 100);
    __ESBMC_ensures(level < 80 || __ESBMC_return_value == 3);
    __ESBMC_ensures(level >= 20 || __ESBMC_return_value == 0);
    __ESBMC_ensures(__ESBMC_return_value >= 0 && __ESBMC_return_value <= 3);
    if (level >= 80)
        return 3;
    if (level >= 50)
        return 2;
    if (level >= 20)
        return 1;
    return 0;
}

/* The liters per second that leave the tank. No clause: the code alone is
   checked (no overflow, division by zero, access out of bounds, or failed
   assert). */
int flow(int liters, int seconds)
{
    return liters / seconds;
}
