// generate waypoints for coverage path planning

// Snow-e
// Engineer: V. J. Hansen
// Compile:  gcc generate_coordinates.c


#include <stdio.h>
#include <math.h>

#define TARGET_POINTS_SIZE 80 // how to find number of target points
#define size_x 10 // height
#define size_z 20 // width
#define delta 0.5


int main () {
    int target_points = 2*(size_z/delta);
    double X_target[target_points];
    double Z_target[target_points];
    float f = 0;
    double w = 0;
    for (int n = 1; n < target_points; n++) {
        f = (-size_x/2.0) * (1 + 3*n + pow(n,2) + 2*(pow(n,3)) - 4*(floor(0.25 * (2+ 3*n + pow(n,2) + 2*(pow(n,3))))));
        X_target[n] = f;
    }
    printf("\n");
    printf("{X, Z}:\n");
    for (int n = 0; n < target_points; n++) {
        w = (-size_z/2.0) + delta*ceil(n/2);
        Z_target[n] = w;
    }
    for (int n = 1; n < target_points; n++) {
        printf("{%.1lf, %.1lf}, ", X_target[n], Z_target[n] );  
    }
    printf("\n");
  return 0;
}