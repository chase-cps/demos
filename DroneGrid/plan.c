/* GridDroneControl, reaction to current_position (MDFS, lf-drone): the move
   a drone asks for, toward its target, horizontal first.
   Moves: 0 stay, 1 right (x + 1), 2 left (x - 1), 3 down (y + 1), 4 up (y - 1).
   plan0 and plan1 are the same controller, with the ports of drone 0 and 1. */

int plan(int x, int y, int tx, int ty)
{
    if (x < tx) return 1;
    if (x > tx) return 2;
    if (y < ty) return 3;
    if (y > ty) return 4;
    return 0;
}

int plan0(int x0, int y0, int tx0, int ty0) { return plan(x0, y0, tx0, ty0); }
int plan1(int x1, int y1, int tx1, int ty1) { return plan(x1, y1, tx1, ty1); }
