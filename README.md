# swot-reach-quicklook
Quicklook plots (WSE/width/slope) for any SWORD reach_id using SWOT Hydrocron (PO.DAAC)


# SWOT River Reach Quicklook (Hydrocron)

This repo is a simple demo notebook that pulls SWOT River reach time series from NASA PO.DAAC Hydrocron and makes quicklook plots for:
- Water Surface Elevation (WSE)
- Width
- Slope

## What’s inside
- `notebooks/01_demo.ipynb` — main demo notebook

## How to run (local)
1) Download/clone the repo
2) Create an environment and install requirements:
```bash
pip install -r requirements.txt

## Run from command line (automatic)
```bash
pip install -r requirements.txt
python run_quicklook.py --reach-id 73218000131
