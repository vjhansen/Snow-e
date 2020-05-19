/*
 * Copyright 1996-2020 Cyberbotics Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 */

/*
 * Description:  This supervisor track the absolute position
 *               of the robot and removes snow from the
 *               area given by the robot
 */

#include <stdlib.h>
#include <webots/display.h>
#include <webots/robot.h>
#include <webots/supervisor.h>

#define TIME_STEP 8

#define X 0
#define Z 2

// size of the ground
#define GROUND_X 4.9
#define GROUND_Z 9.9

int main() {
  wb_robot_init();

  // First we get a handler to devices
  WbDeviceTag display = wb_robot_get_device("ground_display");

  // get the properties of the Display
  int width = wb_display_get_width(display);
  int height = wb_display_get_height(display);

  WbNodeRef mybot = wb_supervisor_node_get_from_def("Snow-e");
  WbFieldRef translationField = wb_supervisor_node_get_field(mybot, "translation");

  // set the background (otherwise an empty ground is displayed at this step)
  WbImageRef background = wb_display_image_load(display, "../../worlds/textures/snow.jpg");
  wb_display_image_paste(display, background, 0, 0, false);

  // set the pen to remove the texture
  wb_display_set_alpha(display, 0.0);

  while (wb_robot_step(TIME_STEP) != -1) {
    // Update the translation field
    const double *translation = wb_supervisor_field_get_sf_vec3f(translationField);

    // display the robot position
    wb_display_fill_oval(display, width * (translation[X] + GROUND_X / 2) / GROUND_X,
                         height * (translation[Z] + GROUND_Z / 2) / GROUND_Z, 15, 15);
  }
  wb_robot_cleanup();
  return 0;
}
