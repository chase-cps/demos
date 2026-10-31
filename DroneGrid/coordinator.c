/* FireCoordinator, reaction to drone_requests (MDFS, lf-drone), for two
   drones: where each drone would be after its move (fx, fy), and the moves
   granted. grant is the reaction as written: when the two drones would
   reach the same cell, or swap cells, while both move, drone 1 stays.
   grant_safe grants a move only into a cell that is free after the step. */

static void future(int x, int y, int r, int *fx, int *fy)
{
    *fx = x;
    *fy = y;
    if (r == 1 && x < 9) *fx = x + 1;
    else if (r == 2 && x > 0) *fx = x - 1;
    else if (r == 3 && y < 9) *fy = y + 1;
    else if (r == 4 && y > 0) *fy = y - 1;
}

void grant(int x0, int y0, int r0, int x1, int y1, int r1,
           int *fx0, int *fy0, int *fx1, int *fy1, int *g0, int *g1)
{
    future(x0, y0, r0, fx0, fy0);
    future(x1, y1, r1, fx1, fy1);
    int collision = 0;
    if (*fx0 == *fx1 && *fy0 == *fy1 && r0 != 0 && r1 != 0)
        collision = 1;                                   /* the same cell */
    else if (*fx0 == x1 && *fy0 == y1 && *fx1 == x0 && *fy1 == y0 && r0 != 0 && r1 != 0)
        collision = 1;                                   /* a swap */
    *g0 = r0;
    *g1 = collision ? 0 : r1;
}

void grant_safe(int x0, int y0, int r0, int x1, int y1, int r1,
                int *fx0, int *fy0, int *fx1, int *fy1, int *g0, int *g1)
{
    future(x0, y0, r0, fx0, fy0);
    future(x1, y1, r1, fx1, fy1);
    /* drone 0 first: not into the cell where drone 1 is now */
    *g0 = (*fx0 == x1 && *fy0 == y1) ? 0 : r0;
    /* drone 1: not into the cell where drone 0 is now, nor where drone 0 goes */
    int at0 = *fx1 == x0 && *fy1 == y0;
    int next0 = *g0 != 0 && *fx1 == *fx0 && *fy1 == *fy0;
    *g1 = (at0 || next0) ? 0 : r1;
}
