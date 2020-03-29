/*
 * File:          avoid_obj.c
 * Date:
 * Description:
 * Author: Victor
 * Modifications:
 */



#include <webots/robot.h>
#include <webots/motor.h>
#include <webots/distance_sensor.h>
#include <stdio.h>


#define TIME_STEP 64
#define MAX_SPEED 6.28


int main(int argc, char **argv) {
  /* necessary to initialize webots stuff */
  wb_robot_init();

  int i;
  WbDeviceTag ps[8];
  
  char ps_names[8][4] = {
    "ps0", "ps1", "ps2", "ps3",
    "ps4", "ps5", "ps6", "ps7",
  };
  
  for (i=0; i<8; i++) {
    ps[i] = wb_robot_get_device(ps_names[i]);
    wb_distance_sensor_enable(ps[i], TIME_STEP);
  }
  
  WbDeviceTag left_motor = wb_robot_get_device("left wheel motor");
  WbDeviceTag right_motor = wb_robot_get_device("right wheel motor");
  wb_motor_set_position(left_motor, INFINITY);
  wb_motor_set_position(right_motor, INFINITY);
  wb_motor_set_velocity(left_motor, 0.0);
  wb_motor_set_velocity(right_motor, 0.0);
    
  while (wb_robot_step(TIME_STEP) != -1) {
    double ps_values[8];
    
    for (i = 0; i < 8 ; i++) {
      ps_values[i] = wb_distance_sensor_get_value(ps[i]);
      printf("sensor value is %f\n", ps_values[i]);
     }

    // detect obstacles
    bool right_obstacle =
      ps_values[0] > 70.0 ||
      ps_values[1] > 70.0 ||
      ps_values[2] > 70.0;
    bool left_obstacle =
      ps_values[5] > 70.0 ||
      ps_values[6] > 70.0 ||
      ps_values[7] > 70.0;
      
    // initialize motor speeds at 50% of MAX_SPEED.
    double left_speed  = 0.5 * MAX_SPEED;
    double right_speed = 0.5 * MAX_SPEED;
    
    // modify speeds according to obstacles
    if (left_obstacle) {
      // turn right
      left_speed  += 0.5 * MAX_SPEED;
      right_speed -= 0.5 * MAX_SPEED;
    }
    else if (right_obstacle) {
      // turn left
      left_speed  -= 0.5 * MAX_SPEED;
      right_speed += 0.5 * MAX_SPEED;
    }

    // write actuators inputs
    wb_motor_set_velocity(left_motor, left_speed);
    wb_motor_set_velocity(right_motor, right_speed);
  }
  wb_robot_cleanup();
  return 0;
}