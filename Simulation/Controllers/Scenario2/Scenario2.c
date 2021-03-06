/*
__Project Description__
  * USN, Campus Kongsberg
  * Snow-e Autonomous Snow Blower
  * Coverage Path Planning using GPS waypoints generated by BCD
  * Scenario 2: one static obstacle with snow

__Version History__
  - Version:      1.1.1
  - Update:       28.05.2020
  - Engineer(s):  V. J. Hansen, D. Kazokas

__Sensors used__
  - Compass:      Navigation
  - GPS:          Generate Zig-Zag path
  - SONAR:        Obstacle detection
  -
*/


/* Webots libraries */
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/compass.h>
#include <webots/distance_sensor.h>
#include <webots/gps.h>
#include <webots/lidar.h>

/* C libraries */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* Macro Definitions */
#define THRESHOLD        900.0
#define TIME_STEP        8
#define NUM_SONAR        8
#define DEFAULT_SPEED    0.5
#define MAX_TURN_SPEED   0.6
#define DELTA            0.3
#define SIZE_Z           10
#define MAXCHAR          2000
#define TURN_COEFFICIENT 0.01

enum FSM { NORMAL, OBSTACLE, DONE };

/* Enum Data Types */
enum SONAR_Sensors { SFL, SBL, SBR, SFR, SFM, SFML, SFMR, SBM };
enum SIDES { LEFT, RIGHT, MIDDLE };
enum XZComponents { X, Y, Z };

/* Webots Sensors */
static WbDeviceTag l_motor, r_motor;
static WbDeviceTag sonar[NUM_SONAR];
static WbDeviceTag compass;
static WbDeviceTag gps;
static WbDeviceTag lidar;

/* Alternative Naming */
typedef struct _Vector
{
  double X_v;
  double Z_u;
} Vector;

char *xfile = "../../Coverage_Planning/x_waypoints_sc2.txt";
char *zfile = "../../Coverage_Planning/z_waypoints_sc2.txt";

static Vector targets[100];
static int num_points   = 0;
static double saved_pos = 0;
static double X_target[MAXCHAR] = {0};
static double Z_target[MAXCHAR] = {0};
double sonar_val[NUM_SONAR] = {0.0, 0.0, 0.0};
double distance = 0.0;
int state = NORMAL;
static int target_index = 1; // = 0 is where we start
double gps_val[2]       = {0.0, 0.0};
double start_gps_pos[3] = {0.0, 0.0, 0.0};

// - read .txt-file
void read_file(char *filename, double *arr_get)
{
  FILE *fp;
  char str[MAXCHAR];
  fp = fopen(filename, "r");
  if (fp == NULL)
  {
      printf("Error: %s",filename);
  }
  int i = 0;
  while (fgets(str, MAXCHAR, fp) != NULL)
  {
    char *token = strtok(str, ",");
    while (token != NULL)
    {
      i++;
      arr_get[i] = atof(token);
      num_points = i;
      token = strtok(NULL, ",");
    }
  }
  fclose(fp);
}

/* Euclidean Norm */
static double norm(const Vector *vec)
{
  return sqrt(vec->Z_u*vec->Z_u + vec->X_v*vec->X_v);
}

// v = v/||v||
static void normalize(Vector *vec)
{
  double n = norm(vec);
  vec->Z_u /= n;
  vec->X_v /= n;
}

// new vector = vector 1 - vector 2
static void minus(Vector *diff, const Vector *trgt, const Vector *gpsPos)
{
  diff->X_v = trgt->X_v - gpsPos->X_v;
  diff->Z_u = trgt->Z_u - gpsPos->Z_u;
}

/*- - - - Initialize robot - - - - - -*/
static void initialize(void)
{
  //..... Boot Message .....
  printf("\nInitializing Snow-e Robot...\n");

  //..... Enable Motors .....
  l_motor = wb_robot_get_device("left motor");
  r_motor = wb_robot_get_device("right motor");
  wb_motor_set_position(l_motor, INFINITY);
  wb_motor_set_position(r_motor, INFINITY);
  wb_motor_set_velocity(l_motor, 0.0);
  wb_motor_set_velocity(r_motor, 0.0);

  //..... Enable Sonar .....
  char sonar_names[NUM_SONAR][10] =
  {
    "Sonar_FL", "Sonar_BL", "Sonar_BR", "Sonar_FR",
    "Sonar_FM", "Sonar_FML", "Sonar_FMR", "Sonar_BM"
  };

  for (int i = 0; i < NUM_SONAR; i++)
  {
    sonar[i] = wb_robot_get_device(sonar_names[i]);
    wb_distance_sensor_enable(sonar[i], TIME_STEP);
  }

  //..... Enable Compass .....
  compass = wb_robot_get_device("compass");
  wb_compass_enable(compass, TIME_STEP);

  //..... Enable GPS .....
  gps = wb_robot_get_device("gps");
  wb_gps_enable(gps, TIME_STEP);
}
/*- - - - - - - - - - - - - - - - - - - - - -*/

/*- - - - - - Autopilot Function - - - - - - */
static int drive_autopilot(void) {
  double Kp = 0.1;
  double Ki = 0.01;
  double speed_max = 0;         // initial speed value
  double distance  = 0;

  static double speed_i  = 0;   // integral value for speed
  static double beta_i   = 0;   // integral value for beta (angle)
  double current_speed_l = wb_motor_get_velocity(l_motor);
  double current_speed_r = wb_motor_get_velocity(r_motor);

  double speed[2]       = {0.0, 0.0};
  double current_time   = wb_robot_get_time();
  const double *north2D = wb_compass_get_values(compass);

  // angle (in degrees) between x and z-axis
  double theta          = atan2(north2D[X], north2D[Z]) * (180/M_PI);

  const double *gps_pos = wb_gps_get_values(gps);

  for (int i = 0; i < NUM_SONAR; i++)
  {
    sonar_val[i] = wb_distance_sensor_get_value(sonar[i]);
  }

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
  if (distance < 2)
  {
    speed_max = 0.2; // Reduce speed to 0.2 m/s
  }

  // Accelerate when 0.5 m away from previous waypoint
  else if (distance > 4 - 0.5)
  {
    speed_max = 0.2;
  }

  // Increase speed to 1 m/s when 0.5 m away from previous waypoint
  else
  {
    speed_max = 1.0;
  }

  // --------------- Calculate PID For Angle and Speed ---------------

  // For Angle
  float beta_e    = ((beta_t - beta_c) * 0.01);
  beta_i          = beta_i + beta_e;
  float PID_beta  = Kp*beta_e + Ki*beta_i;

  // For Speed
  float speed_abs = ((fabs(current_speed_l)+fabs(current_speed_r))/2);
  float speed_e   = (speed_max - speed_abs);
  speed_i         = speed_i + speed_e;
  float PID_speed = Kp*speed_e + Ki*speed_i;
  if (PID_speed < 0)
  {
    PID_speed = 0;
  }
  // --------------- End PID ---------------
  // ---------------------------------------
  switch (state)
  {
    case NORMAL:
      speed[LEFT]  = PID_speed - beta_e;
      speed[RIGHT] = PID_speed + beta_e;
      if (distance <= 0.05)
      {
        printf("Reached Waypoint: %d\n",target_index);
        target_index++;
        speed_i = 0;
        beta_i  = 0;
      }
      else if (target_index == num_points)
      {
        target_index = 1;
      }
      if (fabs(beta_e) > 0.05) // For angles up to 90 degrees
      {
        if (fabs(beta_e) > 0.9) // For angles > 90 degrees
        {
          speed_i       = 0;
          beta_i        = 0;
          speed[LEFT]   = (-PID_beta)*0.5;
          speed[RIGHT]  = (PID_beta)*0.5;
        }
        else
        {
          speed_i       = 0;
          speed[LEFT]   = -PID_beta;
          speed[RIGHT]  =  PID_beta;
        }
      }
      if (sonar_val[SFM]  > THRESHOLD || sonar_val[SFML] > THRESHOLD ||
          sonar_val[SFMR] > THRESHOLD || sonar_val[SFR]  > THRESHOLD ||
          sonar_val[SFL]  > THRESHOLD)
      {
        state     = OBSTACLE;
        saved_pos = gps_pos[Z];
      }
      break;
    case OBSTACLE:
      speed_i   = 0;
      beta_i    = 0;
      PID_speed = 0.20;
      if (targets[target_index-1].Z_u > targets[target_index].Z_u)
      {
        speed[LEFT]  =  PID_speed;
        speed[RIGHT] = -PID_speed;
        if (theta >= -0.5 && theta <= 0.5 && gps_pos[Z] > targets[1].Z_u)
        {
          speed[LEFT]  = PID_speed;
          speed[RIGHT] = PID_speed;
          if (sonar_val[SFR]  < THRESHOLD && sonar_val[SFL]  < THRESHOLD &&
              sonar_val[SBR]  < THRESHOLD && sonar_val[SBL]  < THRESHOLD &&
              sonar_val[SFM]  < THRESHOLD && sonar_val[SBM]  < THRESHOLD &&
              sonar_val[SFML] < THRESHOLD && sonar_val[SFMR] < THRESHOLD &&
              (    fabs(gps_pos[Z]) <= fabs(saved_pos)-1.5*DELTA
                || fabs(gps_pos[Z]) >= fabs(saved_pos)+1.5*DELTA))
          {
           state = NORMAL;
          }
        }
      }
      else if (targets[target_index-1].Z_u <= targets[target_index].Z_u)
      {
        speed[LEFT]  = -PID_speed;
        speed[RIGHT] =  PID_speed;
        if (fabs(theta) >= 179.0 && fabs(theta) <= 181.0 &&
            gps_pos[Z] < targets[num_points-1].Z_u)
        {
          speed[LEFT]  = PID_speed;
          speed[RIGHT] = PID_speed;
          if (sonar_val[SFR]  < THRESHOLD && sonar_val[SFL]  < THRESHOLD &&
              sonar_val[SBR]  < THRESHOLD && sonar_val[SBL]  < THRESHOLD &&
              sonar_val[SFM]  < THRESHOLD && sonar_val[SBM]  < THRESHOLD &&
              sonar_val[SFML] < THRESHOLD && sonar_val[SFMR] < THRESHOLD &&
              (    fabs(gps_pos[Z]) <= fabs(saved_pos)-1.5*DELTA
                || fabs(gps_pos[Z]) >= fabs(saved_pos)+1.5*DELTA))
          {
           state = NORMAL;
          }
        }
      }
      break;
    case DONE:
      speed[LEFT]  = 0.0;
      speed[RIGHT] = 0.0;
      break;
    default:
      break;
    }
  //..... Set Speed .....
  wb_motor_set_velocity(l_motor, speed[LEFT]);
  wb_motor_set_velocity(r_motor, speed[RIGHT]);
  return TIME_STEP;
}
/*- - - - - - - - - - - - - - - - - - -*/


/*- - - - - Main Function - - - - - - -*/
int main(int argc, char **argv)
{
  wb_robot_init();
  initialize();
  read_file(xfile, X_target);
  read_file(zfile, Z_target);

  // fill target-vector with X and Z way points
  for (int i=0, j=1; i<num_points; i++, j++)
  {
    targets[i].X_v = X_target[i];
    targets[i].Z_u = Z_target[j];
  }
  printf("\nStarting Snow-e in Autopilot Mode...\n\n");
  while (wb_robot_step(TIME_STEP) != -1)
  {
    drive_autopilot();
  };
  wb_robot_cleanup();
  return 0;
}
