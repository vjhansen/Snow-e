#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXCHAR 1000
static int num_points = 0;
char *xfile = "x_waypoints.txt";
char *zfile = "z_waypoints.txt";

static double x_arr[MAXCHAR] = {0};
static double z_arr[MAXCHAR] = {0};

void read_file(char *filename, double *arr_get) {
  //double *xres = malloc(MAXCHAR);
  FILE *fp;
  char str[MAXCHAR];
  fp = fopen(filename, "r");
  if (fp == NULL){
      printf("Could not open file %s",filename);
  }
  int i = 0;
  while (fgets(str, MAXCHAR, fp) != NULL) {
    char *token = strtok(str, ",");
    while (token != NULL) {
      i++;
      arr_get[i] = atof(token);
      token = strtok(NULL, ",");
      num_points = i;
    }
  }
  fclose(fp);
}

int main() {
  read_file(xfile, x_arr);
  read_file(zfile, z_arr);
  for (int j=2, i=1; i<num_points; i++, j++) {
    printf("%.2f, %.2f\n", x_arr[i], z_arr[j]);
  }
  return 0;
}
