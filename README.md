## Overview

Like its companion project, **[Shapez-MIP-Router](https://github.com/jiahao-0204/Shapez2-MIP-Router)**, **Shapez2-MIP-Miner** applies Mixed-Integer Programming (MIP) with the Gurobi optimiser to design asteroid-mining layouts that maximise extraction throughput while respecting in-game constraints.

### How to use
1. put screenshot into `/images`
2. edit `path` in `main.py` to point to screenshot
3. `left click` + `right click` to box a repeating element
4. `q` to confirm selection
5. wait for optimizer to run
6. result it shown


### Current Progress Update
> **Status: work in progress – expect rapid changes.**

![Prototype layout screenshot](<images/thumbnail3.png>)


| Symbol          | Meaning              |
|-----------------|----------------------|
| Yellow circle   | Extender platform    |
| Green triangle  | Miner platform       |
| Grey rectangle  | Asteroid source      |
| Blue line       | Space belt           |
| Red cross       | Belt endpoint        |


## Roadmap

- [x] image recognition for importing astroid layouts
- [ ] add yaml file to expose settings
- [ ] better readme (include instruction of git clone, how to star XD, python command etc)
- [ ] better window layout
- [ ] store output to folder
- [ ] spit out shapez blueprint


*Questions or suggestions?* Feel free to open an issue or a pull request.
