#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXCHAR 1000
static int num_points = 0;
char *xfile = "x_waypoints.txt";
char *zfile = "z_waypoints.txt";

double *X_target;
double *Z_target;

double *z_file(char *filename) {
  static double zres[MAXCHAR];
  FILE *fp;
  char str[MAXCHAR];
  printf("%c\n", filename[0]);
  fp = fopen(filename, "r");
  if (fp == NULL){
      printf("Could not open file %s",filename);
  }
  int i = 0;
  while (fgets(str, MAXCHAR, fp) != NULL) {
    char *token = strtok(str, ",");

    while (token != NULL) {
      i++;
      zres[i] = atof(token);
      token = strtok(NULL, ",");
      num_points = i;
    }
  }
  fclose(fp);
  return zres;
}


double *x_file(char *filename) {
  static double xres[MAXCHAR];
  FILE *fp;
  char str[MAXCHAR];
  printf("%c\n", filename[0]);
  fp = fopen(filename, "r");
  if (fp == NULL){
      printf("Could not open file %s",filename);
  }
  int i = 0;
  while (fgets(str, MAXCHAR, fp) != NULL) {
    char *token = strtok(str, ",");

    while (token != NULL) {
      i++;
      xres[i] = atof(token);
      token = strtok(NULL, ",");
      num_points = i;
    }
  }
  fclose(fp);
  return xres;
}


int main() {

  X_target = x_file(xfile);
  Z_target = z_file(zfile);

    for (int i = 1; i <  num_points; i++) {
      printf("%f, %f \n", X_target[i], Z_target[i+1]);
    }
    return 0;
}
