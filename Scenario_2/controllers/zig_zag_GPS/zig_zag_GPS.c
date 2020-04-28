// USN Kongsberg
// Scenario 2 - Static obstacles

/* Snow-e Autonomous Snow Blower
   Dynamic Coverage Path Planning using GPS */

/*  
  - Version: 0.2.2
  - Date: 28.04.2020
  - Engineers: V. J. Hansen
*/

/*
To do:
  - Add LiDAR to enable 360 obstacle detection
  - Add snow plow/shredder and chute
*/

/*  Sensors used:
  - Sonar: detect obstacles
  - Compass: navigation
  - GPS: Generate Zig-Zag path 
*/

/*--------------------------------------------------------*/ 
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/distance_sensor.h>
#include <webots/compass.h>
#include <webots/keyboard.h>
#include <webots/gps.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
/*--------------------------------------------------------*/ 
#define THRESHOLD     900.0
#define TIME_STEP     8
#define NUM_SONAR     3
#define DEFAULT_SPEED 0.1
#define DELTA         0.7
#define SIZE_X        4
#define SIZE_Z        19 
/*--------------------------------------------------------*/ 
enum SIDES { LEFT, RIGHT, MIDDLE };
enum FSM { INIT, FORWARD, PAUSE, GO_LEFT, GO_RIGHT, UTURN_R, UTURN_L, OBSTACLE, STUCK, DONE };
enum SONAR_Sensors { SONAR_MID, SONAR_L, SONAR_R };
enum XZComponents { X, Y, Z };
/*--------------------------------------------------------*/ 
typedef struct _Vector {
  double X_v;
  double Z_v;
} Vector;
/*--------------------------------------------------------*/ 
static WbDeviceTag sonar[NUM_SONAR];
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag compass;
static WbDeviceTag gps;
/*--------------------------------------------------------*/ 
static Vector targets[100];
double *Z_target, *X_target;
double sonar_val[NUM_SONAR] = {0.0, 0.0, 0.0};
double gps_val[2] = {0.0, 0.0};
double start_gps_pos[3] = {0.0, 0.0, 0.0};
int state = INIT;
int new_north = 90;
double distance = 0.0;
static double saved_z, saved_x = 0.0;
static bool autopilot = true;
static bool old_autopilot = true;
static bool obs_flag = false;
static int old_key = -1;
static int target_index = 1; // = 0 is where we start
int target_points = 2*(SIZE_Z/DELTA);
/*--------------------------------------------------------*/ 
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
/*--------------------------------------------------------*/ 
double *generate_x(int num_points) {
    static double x[100];
    for (int n = 0; n < num_points; n++) {
        x[n] = (-SIZE_X/2.0) * (1 + 3*n + pow(n,2) + 2*(pow(n,3)) - 4*(floor(0.25 * (2+ 3*n + pow(n,2) + 2*(pow(n,3))))));
    }
    return x;
}
/*--------------------------------------------------------*/ 
double *generate_z(int num_points) {
    static double z[100];
    for (int n = 0; n < num_points; n++) {
        z[n] = (-SIZE_Z/2.0) + DELTA*ceil(n/2);
    }
    return z;
}
/*--------------------------------------------------------*/ 
// Euclidean Norm, i.e. distance between 
static double norm(const Vector *vec) {
  return sqrt(vec->Z_v*vec->Z_v + vec->X_v*vec->X_v);
}
/*--------------------------------------------------------*/ 
// new vector = vector 1 - vector 2
static void minus(Vector *diff, const Vector *trgt, const Vector *gpsPos) {
  diff->X_v = trgt->X_v - gpsPos->X_v;
  diff->Z_v = trgt->Z_v - gpsPos->Z_v;
}
/*--------------------------------------------------------*/ 
static int drive_autopilot(void) {
  double speed[2] = {0.0, 0.0};  
  double current_time = wb_robot_get_time();
  const double *north2D = wb_compass_get_values(compass);
  double theta = atan2(north2D[X], north2D[Z]) * (180/M_PI); // angle (in degrees) between x and z-axis 
  const double *gps_pos = wb_gps_get_values(gps);
  
  Vector curr_gps_pos = {gps_pos[X], gps_pos[Z]};
  Vector dir; 
  minus(&dir, &targets[target_index], &curr_gps_pos); 
  distance = norm(&dir);
  
  // get sonar values
  for (int i=0; i<NUM_SONAR; i++) {
    sonar_val[i] = wb_distance_sensor_get_value(sonar[i]);
  }
  
  // used for calibration
  if (fmod(current_time, 2) == 0.0) {
    printf("(angle) = (%.4g)\n", theta);
    printf("(dist)  = (%.4g)\n", distance);
    printf("(X_s)  = (%.4g)\n", saved_x);
    printf("(Z_s)  = (%.4g)\n", saved_z);
  }

  if (distance <= 1.1) {
    target_index++;
  }
  
/*----------------------------*/ 
  switch (state) {
    /*...... GET the x-direction (North/South) the robot is pointing to initially ......*/ 
    case INIT:
      new_north = (int)theta;
      state = FORWARD;
      break;
/*--------------FORWARD--------------*/
    case FORWARD:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      if (sonar_val[SONAR_MID] > THRESHOLD) {
        saved_z = gps_pos[Z];
        saved_x = gps_pos[X];
        state = OBSTACLE;
      }
      // Going North
      else if (new_north >= 89 && new_north <= 91 && target_index > 2 && obs_flag == false) {
        if (gps_pos[X] >= X_target[target_index]) {
          state = PAUSE;
        }
      }
      // Going South
      else if (new_north >= -91 && new_north <= -89) {
        if (gps_pos[X] <= X_target[target_index]) {
          state = PAUSE;
        }
      }
      else if (target_index == target_points-1) {
        state = DONE;
      }
      /*----------------------------*/ 
      else if (target_index < 2 && gps_pos[X] >= saved_x+2 && gps_pos[Z] >= saved_z && obs_flag == false) {
        state = GO_LEFT;   // saved_x + "height" of object
      }
      
      else if (obs_flag == true) {
        if (gps_pos[X] >= saved_x+2) {
        state = GO_RIGHT; 
        }
        
      }
      /*----------------------------*/ 
      break;
      
/*--------------PAUSE--------------*/ 
    case PAUSE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
      // going north
      if (new_north >= 89 && new_north <= 91) {
        state = GO_RIGHT;
      }
      // going south
      else if (new_north >= -91 && new_north <= -89) {
        state = GO_LEFT;
      }
      break;    
/*--------------GO LEFT--------------*/ 
    case GO_LEFT:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      
      if (obs_flag == true && target_index > 2) {
        if (fabs(theta) <= 2.0) {
         speed[LEFT]  = DEFAULT_SPEED;
         speed[RIGHT] = DEFAULT_SPEED;
          if (gps_pos[Z] <= Z_target[target_index]-1.5) { // -Z_0
            state = UTURN_R;
          }
        }
      }
      /*----------------------------*/ 
      if (target_index < 2) { // special case
        if (fabs(theta) <= 2.0) { // east
          speed[LEFT]  = DEFAULT_SPEED;
          speed[RIGHT] = DEFAULT_SPEED;
          if (gps_pos[Z] <= Z_target[target_index]) { // -Z_0
            state = UTURN_R;
          }
        }
      }
      /*----------------------------*/ 
      else if (target_index > 2 && fabs(theta) >= 179.0 && fabs(theta) <= 181.0) {
         speed[LEFT]  = DEFAULT_SPEED;
         speed[RIGHT] = DEFAULT_SPEED;
         if (gps_pos[Z] >= Z_target[target_index] && target_index >= 3 && gps_pos[X] <= X_target[target_index]) {
           state = UTURN_L;
         }
         else if (gps_pos[Z] >= saved_z+2*DELTA && target_index == 3) { // special case
           state = GO_RIGHT;
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
         /*----------------------------*/ 
         if (target_index < 2 && gps_pos[Z] >= saved_z+DELTA+0.2) { // special case
         // saved_z + "width" of object
           state = UTURN_L;
         }
         /*----------------------------*/ 
         else if (gps_pos[Z] >= Z_target[target_index] && target_index > 2) {
           state = UTURN_R;
         }
      }
      break;
/*--------------UTURN RIGHT--------------*/
    case UTURN_R:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      /*----------------------------*/ 
      if (target_index < 2) { // special case
        if (theta >= 89.0 && theta <= 91.0) {
          new_north = 90;
          obs_flag = true;
          state = FORWARD;
        }
      }
      /*----------------------------*/
      else if (obs_flag == true && target_index > 2) {
        if (theta >= 89.0 && theta <= 91.0) {
          new_north = 90;
          state = FORWARD;
        }
      }
      else if (theta >= -91.0 && theta <= -89.0 && obs_flag == false) {
        new_north = -90;
        state = FORWARD;
      }
      break;
/*--------------UTURN LEFT--------------*/   
    case UTURN_L:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      if (theta >= 89.0 && theta <= 91.0) {
        new_north = 90;
        state = FORWARD;
      }
      break;
/*--------------obstacle--------------*/         
    case OBSTACLE:
      /*----------------------------*/ 
      if (target_index < 2) { // special case
        state = GO_RIGHT;
      }
      /*----------------------------*/ 
     else  if (theta >= 89.0 && theta <= 91.0 && target_index > 2) {
        new_north = 90;
        obs_flag = true;
        state = GO_LEFT;
      }
      else if (theta >= -91.0 && theta <= -89.0 && target_index > 2) {
        new_north = -90;
        obs_flag = true;
        state = GO_RIGHT;
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
/*--------------------------------------------------------*/ 
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
}

/*--------------------------------------------------------*/ 
int main(int argc, char **argv) {
  wb_robot_init();
  initialize();
  X_target = generate_x(target_points);
  Z_target = generate_z(target_points);
  
  // fill target-vector with X and Z way points
  for (int i = 0; i < target_points; i++) {
    targets[i].X_v = X_target[i];
    targets[i].Z_v = Z_target[i];
  }

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