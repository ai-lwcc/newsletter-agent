# Setup Guide

## Requirements

- Ubuntu
- Python 3
- PostgreSQL
- Redis
- VS Code

## Installation

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib redis-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt