# Motion Planning

## Python

Python code for several path planning algorithms is located inside
[python_src](https://github.com/RuslanAgishev/motion_planning/tree/master/python_src) folder.
Let's go through a couple of examples.

 
### Coverage Path Planning
Exploration of the environment with unknown obstacles location. Random walk algorithm implementation for a mobile robot
equipped with 4 ranger sensors (front, back, left and right) for obstacles detection. An example of a robot with similar sensors setup could a Crazyflie drone with a [multiranger](https://www.bitcraze.io/products/multi-ranger-deck/) deck mounted.
```bash
python python_src/exploration/random_goals_following/main.py
```
```bash
python python_src/exploration/random_walk/main.py
```
<img src="https://github.com/RuslanAgishev/motion_planning/blob/master/figures/exploration/autonomous_exploration.gif" width="400"/> <img src="https://github.com/RuslanAgishev/motion_planning/blob/master/figures/exploration/random_walk.png" width="400"/>

Coverage path planning for unknown map exploration. Robot's kinematics is taken into account in velocity motion model.
```bash
python python_src/exploration/coverage_path_planning/main3D.py
```
<img src="https://github.com/RuslanAgishev/motion_planning/blob/master/figures/coverage_path_planning/cpp_3D_view.png" width="500"/>
