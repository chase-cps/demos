/* GridDroneSim, reaction to move_command (MDFS, lf-drone): the cell of the
   drone after the move granted, on a 10 x 10 grid. */

void move(int x, int y, int g, int *nx, int *ny)
{
    *nx = x;
    *ny = y;
    if (g == 1 && x < 9) *nx = x + 1;
    else if (g == 2 && x > 0) *nx = x - 1;
    else if (g == 3 && y < 9) *ny = y + 1;
    else if (g == 4 && y > 0) *ny = y - 1;
}

void move0(int x0, int y0, int g0, int *nx0, int *ny0) { move(x0, y0, g0, nx0, ny0); }
void move1(int x1, int y1, int g1, int *nx1, int *ny1) { move(x1, y1, g1, nx1, ny1); }
