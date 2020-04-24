// generate coordinates 
// gcc gen_coord.c


#include <stdio.h>
#include <math.h>

int main () {
    float f = 0;
    int w = 0;
    printf ("X:\n");
    for (int n = 1; n < 11; n++) {
        f = 1 + 3*n + pow(n,2) + 2*(pow(n,3)) - 4*(floor(0.25* (2+ 3*n + pow(n,2) + 2*(pow(n,3)) ) ) );
        printf ( "%.1lf\n", f );
    }

    printf ( "\n\n\n\n\n");
    printf ("Z:\n");
    for (int n = 0; n < 11; n++) {
        w = ceil(n/2);
        printf ( "%d\n", w );
    }
  return 0;
}