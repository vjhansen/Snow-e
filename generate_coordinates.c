// generate waypoints for coverage path planning

// Snow-e
// Engineer: V. J. Hansen
// Compile:  gcc generate_coordinates.c


#include <stdio.h>
#include <math.h>

#define size_x 10 // height
#define size_z 20 // width
#define delta 0.5


double *generate_x(int num_points) {
    static double x[100];
    for (int n = 0; n < num_points; n++) {
        x[n] = (-size_x/2.0) * (1 + 3*n + pow(n,2) + 2*(pow(n,3)) - 4*(floor(0.25 * (2+ 3*n + pow(n,2) + 2*(pow(n,3))))));
    }
    return x;
}


double *generate_z(int num_points) {
    static double z[100];
    for (int n = 0; n < num_points; n++) {
        z[n] = (-size_z/2.0) + delta*ceil(n/2);
    }
    return z;
}


int main () {
    int target_points = 2*(size_z/delta);
    //double X_target[target_points];
    double *Z_target;
 
    double *X_target;

    X_target = generate_x(target_points);
    Z_target = generate_z(target_points);

    printf("\n");
    printf("{X, Z}:\n");

    for (int n = 0; n < target_points; n++) {
        printf("{%.1lf, %.1lf}, ", X_target[n], Z_target[n] );  
    }
    printf("\n");
  return 0;
}