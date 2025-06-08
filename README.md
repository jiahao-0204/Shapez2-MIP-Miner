## Overview

Like its companion project, **[Shapez-MIP-Router](https://github.com/jiahao-0204/Shapez2-MIP-Router)**, **Shapez2-MIP-Miner** applies Mixed-Integer Programming (MIP) with the Gurobi optimiser to design asteroid-mining layouts that maximise extraction throughput while respecting in-game constraints.

### How to use
1. put screenshot into `/images`
2. edit `path` in `main.py` to point to screenshot
3. `left click` + `right click` to box a repeating element
4. `q` to confirm selection
5. wait for optimizer to run
6. result is shown
7. blueprint code will be printed to console


### Current Progress Update
> **Status: work in progress – expect rapid changes.**

![Prototype layout screenshot](<images/thumbnail3.png>)
![Prototype layout screenshot](<images/result3.png>)
![Prototype layout screenshot](<images/result3_implemented.png>)


| Symbol          | Meaning              |
|-----------------|----------------------|
| Yellow circle   | Extender platform    |
| Green triangle  | Miner platform       |
| Grey rectangle  | Asteroid source      |
| Blue line       | Space belt           |
| Red cross       | Belt endpoint        |


## Roadmap

- [x] image recognition for importing astroid layouts
- [x] spit out shapez blueprint
- [ ] support sending to upper layer
- [ ] add yaml file to expose settings
- [ ] better readme (include instruction of git clone, how to star XD, python command etc)
- [ ] better window layout
- [ ] store output to folder
- [x] make into a web application
  - [x] better blueprint showing box and add copy button
  - [x] add button to adjust peak identification threshold
  - [x] better layout
  - [x] run gorubi as background process so can support multiple users
  - [x] show optimization progress to webpage
  - [ ] dockerise app
  - [ ] test docker locally
  - [ ] ec2 deployment
  - [ ] cloudflare setup
  - [ ] add text box to adjust solver duration
  - [ ] add text box to support custom miner blueprint
  - [ ] toggle between generating fluid miner or shape miner
  - [ ] toggle between single layer and multi layer
  - [ ] a queueing system


*Questions or suggestions?* Feel free to open an issue or a pull request.
