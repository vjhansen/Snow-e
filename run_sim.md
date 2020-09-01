## How to run the simulation in Webots


### Part 0 - Requirements
* Requires [Webots](https://www.cyberbotics.com/) Open-Source Robot Simulator
* `git clone https://github.com/vjhansen/Snow-e.git`
* `cd Snow-e/`
* `pip3 install -r requirements.txt` or `pip install -r requirements.txt`


### Part 1 - Python Scripts
* `cd Snow-e/Simulation/Coverage_Planning/Resources/`
* run `python3 image_to_binary_map.py --image sim_lot.png`
* run `python3 main_BCD.py -i [binary map] [height of parking lot] [width of parking lot] [side step (i.e. delta)]`
* e.g. `python3 main_BCD.py -i new_map_sc1.png 5 10 0.3  `

### Part 2 - Webots 
* Go to `Snow-e/Simulation/Worlds`
* Click on one of the `.wbt`-files. E.g. `scenario2.wbt` which includes an obstacle.
* Collapse the `DEF Snow-e Robot` section
* Scroll down to `controller "Scenario "`, Select `Scenario1` or `Scenario2` depending on the world you are in.
* Click `Edit` to open the Text Editor.
* `Build` the controller.
