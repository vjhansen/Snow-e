/*
__Project Description__
  * USN, Campus Kongsberg
  * Snow-e Autonomous Snow Blower
  * Coverage Path Planning using GPS waypoints generated by BCD
  * Scenario 1: No Obstacles

__Version History__
  - Version:      1.1.0
  - Update:       26.05.2020
  - Engineer(s):  V. J. Hansen, D. Kazokas

__Sensors used__
  - Compass:      Navigation
  - GPS:          Generate Zig-Zag path
*/


/* Webots libraries */
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/compass.h>
#include <webots/gps.h>

/* C libraries */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Macro Definitions */
#define delta       0.3
#define size_x      5
#define size_z      10
#define MAXCHAR     1000

/* Enum Data Types */
enum SIDES { LEFT, RIGHT, MIDDLE };
enum XZComponents { X, Y, Z };

/* Webots Sensors */
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag compass;
static WbDeviceTag gps;

/* Alternative Naming */
typedef struct _Vector {
  double X_v;
  double Z_u;
} Vector;

char *xfile = "../../../Coverage_Planning/x_waypoints_sc1.txt";
char *zfile = "../../../Coverage_Planning/z_waypoints_sc1.txt";
int TIME_STEP = 8;
static Vector targets[100];
static int num_points = 0;
static double X_target[MAXCHAR] = {0};
static double Z_target[MAXCHAR] = {0};
static int target_index = 1; // = 0 is where we start
double gps_val[2] = {0.0, 0.0};
double start_gps_pos[3] = {0.0, 0.0, 0.0};

// - read .txt-file
void read_file(char *filename, double *arr_get) {
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
      num_points = i;
      token = strtok(NULL, ",");
    }
  }
  fclose(fp);
}

/* Euclidean Norm */
static double norm(const Vector *vec) {
  return sqrt(vec->Z_u*vec->Z_u + vec->X_v*vec->X_v);
}

// v = v/||v||
static void normalize(Vector *vec) {
  double n = norm(vec);
  vec->Z_u /= n;
  vec->X_v /= n;
}

// new vector = vector 1 - vector 2
static void minus(Vector *diff, const Vector *trgt, const Vector *gpsPos) {
  diff->X_v = trgt->X_v - gpsPos->X_v;
  diff->Z_u = trgt->Z_u - gpsPos->Z_u;
}

/*- - - - Initialize robot - - - - - -*/
static void initialize(void) {
  //..... Boot Message .....
  printf("\nInitializing Snow-e Robot...\n");

  //..... Enable Motors .....
  l_motor = wb_robot_get_device("left motor");
  r_motor = wb_robot_get_device("right motor");
  wb_motor_set_position(l_motor, INFINITY);
  wb_motor_set_position(r_motor, INFINITY);
  wb_motor_set_velocity(l_motor, 0.0);
  wb_motor_set_velocity(r_motor, 0.0);

  //..... Enable Compass .....
  compass = wb_robot_get_device("compass");
  wb_compass_enable(compass, TIME_STEP);

  //..... Enable GPS .....
  gps = wb_robot_get_device("gps");
  wb_gps_enable(gps, TIME_STEP);
}
/*- - - - - - - - - - - - - - - - - - - - - - - -*/

/*- - - - -  Autopilot Function - - - - - - - - -*/
static int drive_autopilot(void) {
  float Kp = 0.1;
  float Ki = 0.01;
  float speed_max = 0;        // initial speed value
  float distance  = 0;
  static float speed_i = 0;   // integral value for speed
  static float beta_i  = 0;   // integral value for beta (angle)
  float current_speed_l = wb_motor_get_velocity(l_motor);
  float current_speed_r = wb_motor_get_velocity(r_motor);

  double speed[2] = {0.0, 0.0};
  const double *north2D = wb_compass_get_values(compass);
  const double *gps_pos = wb_gps_get_values(gps);

  Vector north = {north2D[X], north2D[Z]};
  Vector front = {north.X_v, -north.Z_u};
  Vector curr_gps_pos = {gps_pos[X], gps_pos[Z]};
  Vector dir;
  minus(&dir, &targets[target_index], &curr_gps_pos);
  distance = norm(&dir);
  normalize(&dir);

  // Compute target angle
  float beta_t = atan2(dir.X_v, dir.Z_u) * (180/M_PI);
  // Compute current angle
  float beta_c = atan2(front.X_v, front.Z_u) * (180/M_PI);

  // --------------- Speed Constraints ---------------
  if (distance < 2) {speed_max = 0.2;} // Reduce speed to 0.2m/s

  // Accelerate when 0.5m away from previous waypoint
  else if (distance > size_x - 0.5) {speed_max = 0.2;}

  // Increase speed to 1m/s when 0.5m away from previous waypoint
  else{speed_max = 1.0;}

  // --------------- Calculate PID for Angle and Speed ---------------
  // For Angle
  float beta_e = ((beta_t - beta_c) * 0.01);
  beta_i = beta_i + beta_e;
  float PID_beta = Kp*beta_e + Ki*beta_i;
  // For Speed
  float speed_abs = ((fabs(current_speed_l)+fabs(current_speed_r))/2);
  float speed_e = (speed_max - speed_abs);
  speed_i = speed_i + speed_e;
  float PID_speed = Kp*speed_e + Ki*speed_i;
  if (PID_speed < 0) {PID_speed = 0;}
  // --------------- End PID ---------------

  //  Approach the waypoints and reset the integrals
  if (distance <= 0.05) {
    printf("Reached Waypoint: %d\n",target_index);
    target_index++;
    speed_i = 0;
    beta_i = 0;
  }
  else if (target_index == num_points) {
    target_index = 1; // go back to first waypoint
    //TIME_STEP = -1; // stops simulation at last waypoint
  }

  //..... Set Speed According to Angle.....
  if (fabs(beta_e) > 0.05){  // For angles up to 90 degrees
    if (fabs(beta_e) > 0.9){ // For larger angles than 90 degrees
      speed_i = 0;
      beta_i = 0;
      speed[LEFT]  = (-PID_beta)*0.5;
      speed[RIGHT] = (PID_beta)*0.5;
    }
    else{
      speed_i = 0;
      speed[LEFT]  = -PID_beta;
      speed[RIGHT] =  PID_beta;
    }
  }
  else{
    speed[LEFT]  = PID_speed - beta_e;
    speed[RIGHT] = PID_speed + beta_e;
  }
  wb_motor_set_velocity(l_motor, speed[LEFT]);
  wb_motor_set_velocity(r_motor, speed[RIGHT]);
  return TIME_STEP;
}
/*- - - - - - - - - - - - - - - - - - - - - - - -*/

/*- - - - - - - - -  Main Function - - - - - - - */
int main(int argc, char **argv) {
  wb_robot_init();
  initialize();
  read_file(xfile, X_target);
  read_file(zfile, Z_target);

  // fill target-vector with X and Z way points
  for (int i=0, j=1; i<num_points; i++, j++) {
    targets[i].X_v = X_target[i];
    targets[i].Z_u = Z_target[j];
  }
  printf("\nStarting Snow-e in Autopilot Mode...\n\n");
  while (wb_robot_step(TIME_STEP) != -1) {
    drive_autopilot();
  };
  wb_robot_cleanup();
  return 0;
}
