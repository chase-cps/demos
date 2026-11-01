/* The next slot of a ring buffer of 8 slots: its contract in the clauses
   of CBMC. */

void advance(int i, int *ni)
    __CPROVER_requires(i >= 0 && i <= 7)
    __CPROVER_requires(__CPROVER_is_fresh(ni, sizeof(int)))
    __CPROVER_assigns(*ni)
    __CPROVER_ensures(*ni >= 0 && *ni <= 7)
    __CPROVER_ensures(i == 7 || *ni == i + 1)
{
    if (i < 7) *ni = i + 1;
    else *ni = 0;
}

/* The same without the wrap at the end of the buffer: the contract says
   the slot stays in the buffer, and it does not. */
void advance_fast(int i, int *ni)
    __CPROVER_requires(i >= 0 && i <= 7)
    __CPROVER_requires(__CPROVER_is_fresh(ni, sizeof(int)))
    __CPROVER_assigns(*ni)
    __CPROVER_ensures(*ni >= 0 && *ni <= 7)
{
    *ni = i + 1;
}
