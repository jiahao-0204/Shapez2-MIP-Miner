# Astroid Planner

An optimizer for asteroid mining layouts in **Shapez 2** using Mixed-Integer Programming (MIP) with Gurobi.

---

## 🧭 Navigation Reference

| Section | Links |
| --- | --- |
| **⚡ Quick Start** | [🌐 Try Online](#-try-online) • [💻 Install Locally](#-install-locally) • [☁️ Deploy on AWS](#%EF%B8%8F-deploy-on-aws) |
| **📚 Learn More** | [📖 What is This?](#-what-is-this) • [🔧 Optimization Details](#-optimization-details) • [🔌 API Endpoints](#-api-endpoints) • [🔗 Related Projects](#-related-projects) |
| **🤝 Contribute** | [🐛 Contributing](#-contributing) • [📄 License](#-license) |
---

## 📖 What is This?

Astroid Planner solves the asteroid mining layout optimization problem. Given a set of asteroids you want to mine, the tool automatically determines the optimal placement of the following components to maximize the number of asteroids mined:

* **Miners** (extract resources)
* **Extenders** (extend miner reach)
* **Belts** (route resources)
* **Elevators** (send to Layer 1)

---

## 🌐 Try Online

Use the web version at **[shapez2-tools.com](https://shapez2-tools.com)** — no installation needed!

### Features

* **Web Interface**: Real-time streaming solver output.
* **Multi-user**: Background threads handle concurrent optimizations.
* **Task Management**: Auto-cleanup after 15 minutes, maximum 5-minute solver runs.
* **Solver Options**: Add elevators to Layer 1, use custom miner blueprints, convert shape miners to fluid miners, remove non-saturated miners, and adjust solver time limits.
* **QR Encoder**: Generate QR codes as Shapez blueprints.
* **Statistics**: Track total/daily tasks and concurrent solvers.

### Usage Steps

1. Go to [shapez2-tools.com](https://shapez2-tools.com).
2. Copy the "Brush Blueprint" (10×10 template).
3. Paste into Shapez 2, then `Shift+Drag` to place miners on asteroids.
4. Copy all miner blueprints and paste them into the tool.
5. Click "Run Solver" and wait for the results.
6. Paste the generated blueprint back into the game.

### Visualization Legend

| Icon | Color | Element |
| --- | --- | --- |
| 🟡 | Yellow | Extender platform |
| 🟢 | Green | Miner platform |
| ⬜ | Grey | Asteroid source |
| 🔵 | Blue | Space belt |
| ❌ | Red | Belt endpoint |

---

## 💻 Install Locally

### Prerequisites

* Gurobi (Free for students/academics, or a 30-day trial available at [gurobi.com](https://www.gurobi.com)).

### Installation

```bash
git clone https://github.com/jiahao-0204/Shapez2-MIP-Miner
cd Shapez2-MIP-Miner

# Create environment
conda create -n shapez2
conda activate shapez2

# Install dependencies
conda install gurobi opencv scikit-image matplotlib uvicorn colorlog qrcode
conda install -c conda-forge segno

```

### Running Locally

```bash
cd app
uvicorn webapp:app --host 0.0.0.0 --port 8000 --reload

```

> **Note:** Once running, open `http://localhost:8000` in your browser.

### Project Structure

| Path | Description |
| --- | --- |
| `app/webapp.py` | FastAPI endpoints and web server |
| `app/astroid_solver.py` | Gurobi MIP model and solver |
| `app/astroid_parser.py` | Parse blueprints, extract asteroid locations |
| `app/blueprint_composer.py` | Build blueprints from solution |
| `app/qr_encoder.py` | QR code generation tool |
| `app/templates/` | UI templates (`index.html` and `qr_encoder.html`) |
| `app/custom_logging/` | Logging setup |
| `server/` | Deployment configs (systemd, nginx) |
| `images/` | Example screenshots |

---

## ☁️ Deploy on AWS

**Step 1: Environment Setup**

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

conda create -n shapez2
conda activate shapez2
conda install gurobi opencv scikit-image matplotlib uvicorn colorlog qrcode
conda install -c conda-forge segno

```

**Step 2: Clone & Service Installation**

```bash
mkdir ~/git && cd ~/git
git clone https://github.com/jiahao-0204/Shapez2-MIP-Miner
cd Shapez2-MIP-Miner

sudo cp ./server/fastapi.service /etc/systemd/system/
chmod +x ./server/start.sh

sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi

```

**Step 3: Nginx Reverse Proxy Setup**

```bash
sudo apt update
sudo apt install nginx
sudo cp ./server/fastapi.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/fastapi.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

```

**Step 4: HTTPS with Certbot**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d shapez2-tools.com
sudo certbot renew --dry-run

```

**Step 5: DNS Configuration**
Point A records to your instance IP via Cloudflare or your preferred DNS provider.

**Step 6: Memory Management (Swap)**

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

```

### Server Monitoring & Troubleshooting

* **Check Solver Status:** Run `sudo systemctl status fastapi` and `sudo journalctl -u fastapi -f`.
* **Check for OOM (Out of Memory):** Run `sudo journalctl -u fastapi | grep "OOM killer"`.
* **Troubleshoot Memory:** If encountering OOM errors, increase swap space or reduce solver time limits.
* **Troubleshoot Stuck Solver:** Check Gurobi output via `journalctl` or try shorter time limits (the default is 30 seconds).

---

## 🔧 Optimization Details

### Problem Statement

Given specific asteroid locations, the objective is to correctly place elements on a grid:

* **Miners:** Placed at asteroid positions to extract 1 item/s.
* **Extenders:** Placed between miners and destinations to bridge gaps.
* **Belts:** Placed to route items with a maximum flow of 48 items/s.
* **Elevators:** Placed at asteroid positions to send items up to Layer 1.

### Objectives (Multi-objective)

1. **Priority 1 (Higher):** Maximize the total number of miners and extenders.
2. **Priority 2 (Lower):** Maximize fully saturated miners. The solver prefers miners with a flow of 4, followed by 3, 2, and finally 1.

### Constraints

* At most **1 item** may be placed per grid cell (miner, extender, belt, or elevator).
* **Belt flow conservation:** Output must equal input.
* **Extractor flow:** Output must equal input + 1 (generates 1 item).
* **Elevator constraints:** Consumes items (zero outflow).
* **Flow limits:** Maximum belt flow is 48 items/s per direction.
* **Placement limits:** Miners may only be placed on defined asteroid positions.

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| **GET** | `/` | Main solver UI |
| **GET** | `/qr_encoder` | QR encoder UI |
| **GET** | `/get_stats/` | Task statistics |
| **POST** | `/get_simple_coordinates_preview/` | Preview asteroid locations from blueprint |
| **GET** | `/get_task_id/` | Create new optimization task |
| **GET** | `/run_solver_and_stream` | Run optimizer, stream progress (SSE) |
| **POST** | `/get_solver_results` | Get solution visualization |
| **POST** | `/generate_blueprint/` | Generate optimized blueprint |
| **POST** | `/generate_qr_code_image/` | Generate QR code image |
| **POST** | `/generate_qr_code_blueprint/` | Generate QR code as blueprint |

---

## 🔗 Related Projects

* **[Shapez2-MIP-Router](https://github.com/jiahao-0204/Shapez2-MIP-Router)** - Route optimization

---

## 🐛 Contributing
Found a bug or have suggestions? Open an issue or submit a Pull Request!

## 📄 License
See the LICENSE file in the repository for full details.
