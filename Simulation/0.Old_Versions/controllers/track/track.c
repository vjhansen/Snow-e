/*.........................................*/
// !! this version does not determine the Zig-Zag pattern by using GPS coordinates !!
// it uses rotary encoders to measure the distance traversed by the snow blower

//  Snow-e Autonomous Snow Blower 
//  Coverage Path Planning
//  Version 0.8
//  16.04.2020 
//  V. Hansen, D. Kazokas

// - Sonar: detect obstacles
// - Compass: navigation
// - Position Sensors: measure distance travelled
// - GPS: define boundaries


/* To do:
  - Snow on floor
  - Add snow blower module: shredder, chute
  - Obstacle detection
*/


/*.........................................*/
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/distance_sensor.h>
#include <webots/compass.h>
#include <webots/position_sensor.h>
#include <webots/keyboard.h>
#include <webots/gps.h>
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

enum ObstacleFlag { A, B, C };

enum SONAR_Sensors { SONAR_MID, SONAR_L, SONAR_R };
enum XZComponents { X, Y, Z };

/*.........................................*/
static WbDeviceTag sonar[NUM_SONAR];
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag compass;
static WbDeviceTag gps;
static WbDeviceTag l_pos_sens, r_pos_sens;
/*.........................................*/
double sonar_val[NUM_SONAR] = {0.0, 0.0, 0.0};
int state = INIT;
int new_north = 0;
double pos_val[2] = {0.0, 0.0};
double inc_pos = 0.0;
double avg_pos_val = 0.0;
static bool autopilot = true;
static bool old_autopilot = true;
static int old_key = -1;
double gps_val[2] = {0.0, 0.0};

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

/*.........................................*/
static int drive_autopilot(void) {
  double speed[2] = {0.0, 0.0};  
  double current_time = wb_robot_get_time();

  const double *north2D = wb_compass_get_values(compass);
  double theta = atan2(north2D[X], north2D[Z]) * (180/M_PI); // angle (in degrees) between x and z-axis 
  
  const double *gps_pos = wb_gps_get_values(gps);

  // get sonar values
  for (int i=0; i<NUM_SONAR; i++) {
    sonar_val[i] = wb_distance_sensor_get_value(sonar[i]);
  }
  
  pos_val[LEFT]  = wb_position_sensor_get_value(l_pos_sens);
  pos_val[RIGHT] = wb_position_sensor_get_value(r_pos_sens);
  avg_pos_val = (pos_val[LEFT]+pos_val[RIGHT])/2.0;
  
  // used for calibration and debugging
  if (fmod(current_time,2)==0.0) {
    printf("(X, Z) = (%.4g, %.4g)\n", gps_pos[X], gps_pos[Z]);
    printf("%.4g m\n", avg_pos_val);
    printf("%.4g \n", theta);
    //printf("Sonar[M]: %.4g \n",sonar_val[SONAR_MID]);
    //printf("Sonar[L]: %.4g \n",sonar_val[SONAR_L]);
    //printf("Sonar[R]: %.4g \n",sonar_val[SONAR_R]);
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
      if (avg_pos_val >= PATH_LENGTH+inc_pos) {
        state = PAUSE;
      }
      // if snow blower has reached the parking lot boundary
      else if (avg_pos_val >= TOTAL_PATH_LENGTH || fabs(gps_pos[X]) > (AREA/2.0) || fabs(gps_pos[Y]) > (AREA/2.0)) {
        state = DONE;    
      }
      break;
    /*...... PAUSE ......*/ 
    case PAUSE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
      if (new_north > -95 && new_north < -85) { // x-direction = south
        state = GO_RIGHT; 
      }
      else if (new_north > 85 && new_north < 95) { // x-direction = north
        state = GO_LEFT;
      }
      break;
    /*......GO LEFT......*/ 
    // +90 -> 0 degrees
    case GO_LEFT:
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED; 
      if (theta <= 0) {
        speed[LEFT]  = DEFAULT_SPEED;
        speed[RIGHT] = DEFAULT_SPEED;
        if (avg_pos_val >= PATH_LENGTH+TURN_WIDTH+inc_pos) {
          state = UTURN_L;
        }
      }
      break;
    /*......GO RIGHT......*/ 
    // -90 -> 0 degrees
    case GO_RIGHT:
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      if (theta >= 0) {
        speed[LEFT]  = DEFAULT_SPEED;
        speed[RIGHT] = DEFAULT_SPEED;
        if (avg_pos_val >= PATH_LENGTH+TURN_WIDTH+inc_pos) {
          state = UTURN_R;
        }
      }
      break;
    /*......UTURN RIGHT......*/
    case UTURN_R: // from -90 (South) to 90 (North) turn right
      speed[LEFT]  = DEFAULT_SPEED;
      speed[RIGHT] = -DEFAULT_SPEED;
      if (theta > 90) {
        inc_pos = inc_pos+PATH_LENGTH;
        new_north = 90;
        state = FORWARD;
       }
      break;
    /*......UTURN LEFT......*/   
    case UTURN_L: // from 90 (North) to -90 (South) turn left
      speed[LEFT]  = -DEFAULT_SPEED;
      speed[RIGHT] = DEFAULT_SPEED;
      if (theta < -90) {
        inc_pos = inc_pos+PATH_LENGTH;
        new_north = -90;
        state = FORWARD;
      }
      break;
      
    /*......obstacle detected......*/  
    /*case R_OBSTACLE:
      break;
    */
      
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

/*....................................*/
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

  /*......ENABLE POSITION SENSORS......*/
  l_pos_sens = wb_robot_get_device("l_position_sensor");
  r_pos_sens = wb_robot_get_device("r_position_sensor");
  wb_position_sensor_enable(l_pos_sens, TIME_STEP);
  wb_position_sensor_enable(r_pos_sens, TIME_STEP);
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
