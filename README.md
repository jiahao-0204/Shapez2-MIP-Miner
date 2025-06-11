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
  - [x] ec2 deployment
  - [x] add text box to adjust solver duration
  - [x] add text box to support custom miner blueprint
  - [x] parse using blueprint
  - [x] support sending to upper layer
  - [x] optimize for saturated miners
  - [x] don't solve for belts
  - [ ] fix empty miner blueprint not working
  - [ ] dockerise app
  - [ ] test docker locally
  - [ ] cloudflare setup
  - [ ] toggle between generating fluid miner or shape miner
  - [ ] toggle between single layer and multi layer
  - [ ] a queueing system


*Questions or suggestions?* Feel free to open an issue or a pull request.


## EC2 Deployment Notes
- download and install `miniconda`
- `conda create -n shapez2`
- `conda activate shapez2`
- then with `conda install`
  - gurobi
  - opencv
  - scikit-image
  - matplotlib
  - uvicorn-standard
  - colorlog
- to start the webapp
  ```bash
  mkdir git
  cd git
  git clone https://github.com/jiahao-0204/Shapez2-MIP-Miner
  cd Shapez2-MIP-Miner
  sudo cp ./server/fastapi.service /etc/systemd/system/
  chmod +x ./server/start.sh
  sudo systemctl daemon-reload
  sudo systemctl restart fastapi
  sudo systemctl status fastapi
  sudo journalctl -u fastapi -f
  ```
- nginx to port 8000 to 80/443
  ```bash
  sudo apt update
  sudo apt install nginx
  sudo cp ./server/fastapi.conf /etc/nginx/sites-available/
  sudo ln -s /etc/nginx/sites-available/fastapi.conf /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```
- on cloudflare
  - setup DNS "A" record with "@" and "www" that points to server ip address
- certbot to support https
  ```bash
  sudo apt install certbot python3-certbot-nginx
  sudo certbot --nginx -d shapez2-tools.com
  sudo certbot renew --dry-run
  ```
- notes
  - after `sudo cp ./server/fastapi.conf /etc/nginx/sites-available/`, need to redo `sudo certbot --nginx -d shapez2-tools.com`
