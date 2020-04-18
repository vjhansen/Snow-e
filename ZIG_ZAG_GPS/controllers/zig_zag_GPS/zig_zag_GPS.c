/*
To do:

- Add LiDAR to enable 360 obstacle detection
- Generate Zig-Zag patter based on GPS coordinates
- Remove position sensors (i.e. rotary encoders)
- Add snow plow/shredder and chute
- Add snow to surface
- Create new path when encountering obstacles
*/


/* Snow-e Autonomous Snow Blower
   Dynamic Coverage Path Planning using RTK GPS */

/*  
  - Version: 0.0.2
  - Date: 18.04.2020
  - Engineers: V. Hansen, D. Kazokas
*/


/* 
Sensors used:
  - Sonar & LiDAR: detect obstacles
  - Compass: navigation
  - GPS: Generate Zig-Zag path and define boundaries/no go zones
*/


// some functions (norm, minus) are based on concepts from webots/moose_path_following.c

/*.........................................*/
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/distance_sensor.h> // Sonar
#include <webots/compass.h>
#include <webots/keyboard.h>
#include <webots/gps.h>
#include <webots/lidar.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
/*.........................................*/

#define THRESHOLD 900.0
#define TIME_STEP 8
#define NUM_SONAR 3
#define DEFAULT_SPEED 0.1
#define TURN_WIDTH 0.4
#define PATH_LENGTH 7.0
#define TOTAL_PATH_LENGTH 100.0
#define AREA 9.0 // floorSize 10x10


enum SIDES { LEFT, RIGHT, MIDDLE };
enum FSM { INIT, FORWARD, PAUSE, GO_LEFT, GO_RIGHT, 
           UTURN_R, UTURN_L, R_OBSTACLE, STUCK, DONE };


enum SONAR_Sensors { SONAR_MID, SONAR_L, SONAR_R };
enum XZComponents { X, Y, Z };

typedef struct _Vector {
  double Z_v;
  double X_v;
} Vector;


// can hardcode no-go zones here
static Vector hard_code_targets[3] = {
  {-4.209318, -9.147717}, {0.946812, -9.404304},  {0.175989, 1.784311}
};



/*
// Idea - future work: these targets could be generated externally through an app.
static Vector targets[21] = 
{
  {0, 0}, // n = 0
  {0, PATH_LENGTH}, // n = 1
  {TURN_WIDTH, PATH_LENGTH}, 
  {TURN_WIDTH, 0},
  {2*TURN_WIDTH, 0}, 
  {2*TURN_WIDTH, PATH_LENGTH},
  {3*TURN_WIDTH, PATH_LENGTH}, 
  {3*TURN_WIDTH, 0},
  {4*TURN_WIDTH, 0}, 
  {4*TURN_WIDTH, PATH_LENGTH},
  {5*TURN_WIDTH, PATH_LENGTH},
  {5*TURN_WIDTH, 0},
  {6*TURN_WIDTH, 0}, 
  {6*TURN_WIDTH, PATH_LENGTH},
  {7*TURN_WIDTH, PATH_LENGTH}, 
  {7*TURN_WIDTH, 0},
  {8*TURN_WIDTH, 0},
  {8*TURN_WIDTH, PATH_LENGTH},
  {9*TURN_WIDTH, PATH_LENGTH},
  {9*TURN_WIDTH, 0},
  {10*TURN_WIDTH, 0},
}; */

/*.........................................*/
static WbDeviceTag sonar[NUM_SONAR];
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag compass;
static WbDeviceTag gps;

/*.........................................*/

double sonar_val[NUM_SONAR] = {0.0, 0.0, 0.0};
int state = INIT;
int new_north = 0;
double delta = 0.3;
double distance = 0.0;
static bool autopilot = true;
static bool old_autopilot = true;
static int old_key = -1;
double gps_val[2] = {0.0, 0.0};
double start_gps_pos[3] = {0.0, 0.0, 0.0};

/*.........................................*/
static void drive_manual() {
  double speed[2] = {0.0, 0.0};
  int key = wb_keyboard_get_key();
  if (key >= 0) {
    switch (key) {
      case WB_KEYBOARD_UP:
        speed[LEFT]  = DEFAULT_SPEED;
        speed[RIGHT] = DEFAULT_SPEED;
        autopilot = false;
        break;
      case WB_KEYBOARD_DOWN:
        speed[LEFT]  = -DEFAULT_SPEED;
        speed[RIGHT] = -DEFAULT_SPEED;
        autopilot = false;
        break;
      case WB_KEYBOARD_RIGHT:
        speed[LEFT]  = DEFAULT_SPEED;
        speed[RIGHT] = -DEFAULT_SPEED;
        autopilot = false;
        break;
      case WB_KEYBOARD_LEFT:
        speed[LEFT]  = -DEFAULT_SPEED;
        speed[RIGHT] = DEFAULT_SPEED;
        autopilot = false;
        break;
      case 'P':
        if (key != old_key)
          autopilot = !autopilot;
        break;
    }
  }
  if (autopilot != old_autopilot) {
    old_autopilot = autopilot;
    if (autopilot)
      printf("autopilot\n");
    else
      printf("manual control, use WASD.\n");
  }

   /*......SET SPEED......*/
  wb_motor_set_velocity(l_motor, speed[LEFT]);
  wb_motor_set_velocity(r_motor, speed[RIGHT]);
  old_key = key;
}

// Euclidean Norm, i.e. distance between 
static double norm(const Vector *vec) {
  return sqrt(vec->Z_v*vec->Z_v + vec->X_v*vec->X_v);
}

// new vector = vector 1 - vector 2
static void minus(Vector *nv, const Vector *vec1, const Vector *vec2) {
  nv->Z_v = vec1->Z_v - vec2->Z_v;
  nv->X_v = vec1->X_v - vec2->X_v;
}


// v = v/||v||
static void normalize(Vector *vec) {
  double n = norm(vec);
  vec->Z_v /= n;
  vec->X_v /= n;
}


// compute the angle between two vectors
// return value: [0, 2Pi]
static double vector_angle(const Vector *vec1, const Vector *vec2) {
  return fmod(atan2(vec2->X_v, vec2->Z_v) - atan2(vec1->X_v, vec1->Z_v),  2.0*M_PI);
}


// generate target
// current pos + delta
static void generate_target(Vector *tv, const Vector *vec1) {
  tv->Z_v = vec1->Z_v + delta;
  tv->X_v = vec1->X_v + delta;

}
  


/*.........................................*/
static int drive_autopilot(void) {
  double speed[2] = {0.0, 0.0};  
  double current_time = wb_robot_get_time();

  const double *north2D = wb_compass_get_values(compass);
  double theta = atan2(north2D[X], north2D[Z]) * (180/M_PI); // angle (in degrees) between x and z-axis 
  
  const double *gps_pos = wb_gps_get_values(gps);
  Vector curr_gps_pos = {gps_pos[X], gps_pos[Z]};
  
  Vector dir;
  Vector target;
  //generate_target(&target, &curr_gps_pos);
  //minus(&dir, &target, &curr_gps_pos);
  minus(&dir, &hard_code_targets[0], &curr_gps_pos);
  distance = norm(&dir);
  
 
  // get sonar values
  for (int i=0; i<NUM_SONAR; i++) {
    sonar_val[i] = wb_distance_sensor_get_value(sonar[i]);
  }
  
  // used for calibration
  if (fmod(current_time, 2) == 0.0) {
    printf("(X, Z) = (%.4g, %.4g)\n", gps_pos[X], gps_pos[Z]);
    printf("distance: %.4g \n", distance);
  }
    
  /*...... FSM ......*/
  switch (state) {
    /*...... GET the x-direction (North/South) the robot is pointing to initially ......*/ 
    case INIT:
      new_north = (int)theta;
      state = FORWARD;
      break;

    /*......GO FORWARD......*/ 
    case FORWARD:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      generate_target(&target, &curr_gps_pos);
      minus(&dir, &target, &curr_gps_pos);
      distance = norm(&dir);
      break;
    /*...... PAUSE ......*/ 
    case PAUSE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;

      break;
    /*......GO LEFT......*/ 
    case GO_LEFT:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED; 

      break;
    /*......GO RIGHT......*/ 
    case GO_RIGHT:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      break;
    /*......UTURN RIGHT......*/
    case UTURN_R: // from -90 (South) to 90 (North) turn right
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      break;
    /*......UTURN LEFT......*/   
    case UTURN_L: // from 90 (North) to -90 (South) turn left
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      break;

    /*......if we are done with this area......*/ 
    case DONE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
    /*....................................*/  
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
  
  /*......ENABLE KEYBOARD......*/
  wb_keyboard_enable(TIME_STEP);

  /*......ENABLE MOTORS......*/
  l_motor = wb_robot_get_device("left motor");
  r_motor = wb_robot_get_device("right motor");
  wb_motor_set_position(l_motor, INFINITY);
  wb_motor_set_position(r_motor, INFINITY);
  wb_motor_set_velocity(l_motor, 0.0);
  wb_motor_set_velocity(r_motor, 0.0);
  
  /*......ENABLE SONAR......*/
  char sonar_names[NUM_SONAR][5] = {"sfm0", "sfl0", "sfr0"};
  for (int i=0; i<NUM_SONAR; i++) {
    sonar[i] = wb_robot_get_device(sonar_names[i]);
    wb_distance_sensor_enable(sonar[i], TIME_STEP);
  }
  
  /*......ENABLE COMPASS......*/
  compass = wb_robot_get_device("compass");
  wb_compass_enable(compass, TIME_STEP);
  
  /*......ENABLE COMPASS......*/
  gps = wb_robot_get_device("gps");
  wb_gps_enable(gps, TIME_STEP);
}

/*....................................*/ 
int main(int argc, char **argv) {
  wb_robot_init();
  initialize();
  printf("Press 'P' to toggle autopilot/manual mode\n");
  while (wb_robot_step(TIME_STEP) != -1) { 
    drive_manual();
    if (autopilot) {
      drive_autopilot();
    }
  };
  wb_robot_cleanup();
  return 0;
}