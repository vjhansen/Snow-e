![GitHub last commit](https://img.shields.io/github/last-commit/vjhansen/Snow-e)
![GitHub repo size](https://img.shields.io/github/repo-size/vjhansen/Snow-e)
![GitHub](https://img.shields.io/github/license/vjhansen/Snow-e?color=blue)


## Autonomous Snow Blower Simulation - *Snow-e*
>#### Student Project: ES-SES4000 19-20
>#### Engineers: V. J. Hansen, D. Kazokas
---


[![IMAGE ALT TEXT](http://img.youtube.com/vi/GPPK6jh8ui0/0.jpg)](http://www.youtube.com/watch?v=GPPK6jh8ui0 "Autonomous Snow Blower Simulation")


## Run the Simulation

### Part 0 - Requirements
* Requires [Webots](https://www.cyberbotics.com/) Open-Source Robot Simulator
* `pip3 install -r requirements.txt` or `pip install -r requirements.txt`

### Part 1 - Python Scripts
* run `python3 image_to_binary_map.py --image sim_lot.png`
* run `python3 main_BCD.py -i [binary map] [height of parking lot] [width of parking lot] [side step (i.e. delta)]`
* e.g. `python3 main_BCD.py -i new_map_sc1.png 5 10 0.3  `

### Part 2 - Webots 
* add more
