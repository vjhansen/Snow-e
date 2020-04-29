// USN Kongsberg
// Scenario 1

/* Snow-e Autonomous Snow Blower
   Dynamic Coverage Path Planning using GPS */

/*  
  - Version: 0.1.4
  - Update: 29.04.2020
  - Engineer(s): V. J. Hansen
*/


/*  Sensors used:
  - Sonar: detect obstacles
  - Compass: navigation
  - GPS: Generate Zig-Zag path 
*/


/* Webots libraries */
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/distance_sensor.h>
#include <webots/compass.h>
#include <webots/gps.h>
#include <webots/lidar.h>

/* C libraries */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/* macro definitions */
#define THRESHOLD     900.0
#define TIME_STEP     8
#define NUM_SONAR     3
#define DEFAULT_SPEED 0.1
#define delta         0.5
#define size_x        9 
#define size_z        19


enum SIDES { LEFT, RIGHT, MIDDLE };
enum FSM { INIT, FORWARD, PAUSE, GO_LEFT, GO_RIGHT, 
           UTURN_R, UTURN_L, OBSTACLE, DONE };

enum SONAR_Sensors { SONAR_MID, SONAR_L, SONAR_R };
enum XZComponents { X, Y, Z };

typedef struct _Vector {
  double X_v;
  double Z_v;
} Vector;

/*.........................................*/
static WbDeviceTag sonar[NUM_SONAR];
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag compass;
static WbDeviceTag gps;
/*.........................................*/

static Vector targets[100];
double *Z_target;
double *X_target;
double sonar_val[NUM_SONAR] = {0.0, 0.0, 0.0};
int state = INIT;
int front_dir = 90;
double distance = 0.0;
static int target_index = 1; // = 0 is where we start
double gps_val[2] = {0.0, 0.0};
double start_gps_pos[3] = {0.0, 0.0, 0.0};
int target_points = 2*(size_z/delta);


// generate X coordinates
double *generate_x(int num_points) {
    static double x[100];
    for (int n = 0; n < num_points; n++) {
        x[n] = (-size_x/2.0) * (1 + 3*n + pow(n,2) + 2*(pow(n,3)) - 4*(floor(0.25 * (2+ 3*n + pow(n,2) + 2*(pow(n,3))))));
    }
    return x;
}

// generate Z coordinates
double *generate_z(int num_points) {
    static double z[100];
    for (int n = 0; n < num_points; n++) {
        z[n] = (-size_z/2.0) + delta*ceil(n/2);
    }
    return z;
}


// Euclidean Norm, i.e. distance between 
static double norm(const Vector *vec) {
  return sqrt(vec->Z_v*vec->Z_v + vec->X_v*vec->X_v);
}

// new vector = vector 1 - vector 2
static void minus(Vector *diff, const Vector *trgt, const Vector *gpsPos) {
  diff->X_v = trgt->X_v - gpsPos->X_v;
  diff->Z_v = trgt->Z_v - gpsPos->Z_v;
}

/* Autopilot */
static int drive_autopilot(void) {
  double speed[2]       = {0.0, 0.0};  
  double current_time   = wb_robot_get_time();
  const double *north2D = wb_compass_get_values(compass);
  double theta          = atan2(north2D[X], north2D[Z]) * (180/M_PI); // angle (in degrees) between x and z-axis 
  const double *gps_pos = wb_gps_get_values(gps);
  
  Vector curr_gps_pos = {gps_pos[X], gps_pos[Z]};
  Vector dir; 
  minus(&dir, &targets[target_index], &curr_gps_pos); 
  distance = norm(&dir);
  
  // get sonar values
  for (int i = 0; i < NUM_SONAR; i++) {
    sonar_val[i] = wb_distance_sensor_get_value(sonar[i]);
  }
  
  // used for calibration
  if (fmod(current_time, 2) == 0.0) {
    printf("(dist = (%.4g)\n", distance);
  }
  
  if (distance <= 1.1) {
    target_index++;
  }
  
/*----------------------------*/ 
  switch (state) {
    /*...... GET the x-direction (North/South) the robot is pointing to initially ......*/ 
    case INIT:
      front_dir = (int)theta;
      state = FORWARD;
      break;
/*--------------FORWARD--------------*/
    case FORWARD:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      // Going North
      if (front_dir >= 89 && front_dir <= 91) {
        if (gps_pos[X] >= X_target[target_index]) {
          state = PAUSE;
        }
      }
      // Going South
      else if (front_dir >= -91 && front_dir <= -89) {
        if (gps_pos[X] <= X_target[target_index]) {
          state = PAUSE;
        }
      }
      else if (target_index == target_points-1) {
        state = DONE;
      }
      break;
      
/*--------------PAUSE--------------*/ 
    case PAUSE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
      // going north
      if (front_dir >= 89 && front_dir <= 91) {
        state = GO_RIGHT;
      }
      // going south
      else if (front_dir >= -91 && front_dir <= -89) {
        state = GO_LEFT;
      }
      break;
      
/*--------------GO LEFT--------------*/ 
    case GO_LEFT:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      if (fabs(theta) >= 179.0 && fabs(theta) <= 181.0) {
         speed[LEFT]  = DEFAULT_SPEED;
         speed[RIGHT] = DEFAULT_SPEED;
         if (gps_pos[Z] >= Z_target[target_index] && gps_pos[X] <= X_target[target_index]) {
           state = UTURN_L;
         }
      }
      break;
/*--------------GO RIGHT--------------*/ 
    case GO_RIGHT:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      if (fabs(theta) >= 179.0 && fabs(theta) <= 181.0) {
         speed[LEFT]  = DEFAULT_SPEED;
         speed[RIGHT] = DEFAULT_SPEED;
         if (gps_pos[Z] >= Z_target[target_index]) {
           state = UTURN_R;
         }
      }
      break;
/*--------------UTURN RIGHT--------------*/
    case UTURN_R:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      if (theta >= -91.0 && theta <= -89.0) {
        front_dir = -90;
        state = FORWARD;
      }
      break;
/*--------------UTURN LEFT--------------*/   
    case UTURN_L:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      if (theta >= 89.0 && theta <= 91.0) {
        front_dir = 90;
        state = FORWARD;
      }
      break;
/*......if we are at the last target......*/ 
    case DONE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
/*------------------------------------------*/  
    default:
      break;
  }
  /*......SET SPEED......*/
  wb_motor_set_velocity(l_motor, speed[LEFT]);
  wb_motor_set_velocity(r_motor, speed[RIGHT]);
  return TIME_STEP;
}

static void initialize(void) {
  printf("booting robot..\n");  

  /*......ENABLE MOTORS......*/
  l_motor = wb_robot_get_device("left motor");
  r_motor = wb_robot_get_device("right motor");
  wb_motor_set_position(l_motor, INFINITY);
  wb_motor_set_position(r_motor, INFINITY);
  wb_motor_set_velocity(l_motor, 0.0);
  wb_motor_set_velocity(r_motor, 0.0);
  
  /*......ENABLE SONAR......*/
  char sonar_names[NUM_SONAR][5] = {"sfm0", "sfl0", "sfr0"};
  for (int i = 0; i < NUM_SONAR; i++) {
    sonar[i] = wb_robot_get_device(sonar_names[i]);
    wb_distance_sensor_enable(sonar[i], TIME_STEP);
  }
  
  /*......ENABLE COMPASS......*/
  compass = wb_robot_get_device("compass");
  wb_compass_enable(compass, TIME_STEP);
  
  /*......ENABLE GPS......*/
  gps = wb_robot_get_device("gps");
  wb_gps_enable(gps, TIME_STEP);
  
  /*......ENABLE LIDAR......*/
  WbDeviceTag lidar = wb_robot_get_device("lidar");
  wb_lidar_enable(lidar, TIME_STEP);
  wb_lidar_enable_point_cloud(lidar);
  
}

/*....................................*/ 
int main(int argc, char **argv) {
  wb_robot_init();
  initialize();
  X_target = generate_x(target_points);
  Z_target = generate_z(target_points);
  
  // fill target-vector with X and Z way points
  for (int i=0; i<target_points; i++) {
    targets[i].X_v = X_target[i];
    targets[i].Z_v = Z_target[i];
  }

  while (wb_robot_step(TIME_STEP) != -1) { 
      drive_autopilot();
  };
  wb_robot_cleanup();
  return 0;
}