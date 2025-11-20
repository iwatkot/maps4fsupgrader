<div align="center" markdown>

[![Maps4FS](https://img.shields.io/badge/maps4fs-gray?style=for-the-badge)](https://github.com/iwatkot/maps4fs)
[![PYDTMDL](https://img.shields.io/badge/pydtmdl-blue?style=for-the-badge)](https://github.com/iwatkot/pydtmdl)
[![PYGDMDL](https://img.shields.io/badge/pygmdl-teal?style=for-the-badge)](https://github.com/iwatkot/pygmdl)  
[![Maps4FS API](https://img.shields.io/badge/maps4fs-api-green?style=for-the-badge)](https://github.com/iwatkot/maps4fsapi)
[![Maps4FS UI](https://img.shields.io/badge/maps4fs-ui-blue?style=for-the-badge)](https://github.com/iwatkot/maps4fsui)
[![Maps4FS Data](https://img.shields.io/badge/maps4fs-data-orange?style=for-the-badge)](https://github.com/iwatkot/maps4fsdata)
[![Maps4FS ChromaDocs](https://img.shields.io/badge/maps4fs-chromadocs-orange?style=for-the-badge)](https://github.com/iwatkot/maps4fschromadocs)  
[![Maps4FS Upgrader](https://img.shields.io/badge/maps4fs-upgrader-yellow?style=for-the-badge)](https://github.com/iwatkot/maps4fsupgrader)
[![Maps4FS Stats](https://img.shields.io/badge/maps4fs-stats-red?style=for-the-badge)](https://github.com/iwatkot/maps4fsstats)
[![Maps4FS Bot](https://img.shields.io/badge/maps4fs-bot-teal?style=for-the-badge)](https://github.com/iwatkot/maps4fsbot)

</div>

<div align="center">

<img src="https://github.com/iwatkot/maps4fsupgrader/releases/download/0.1.3/upgrader-1280-640.png">

<p align="center">
    <a href="#overview">Overview</a> •
    <a href="#supported-containers">Supported Containers</a> •
    <a href="#prerequisites">Prerequisites</a> •
    <a href="#usage">Usage</a><br>
    <a href="#configuration">Configuration</a> •
    <a href="#directory-structure">Directory Structure</a> •
    <a href="#logging">Logging</a> •
    <a href="#development">Development</a><br>
</p>

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/iwatkot/maps4fsupgrader)](https://github.com/iwatkot/maps4fsupgrader/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/iwatkot/maps4fsupgrader)](https://hub.docker.com/repository/docker/iwatkot/maps4fsupgrader/general)
[![GitHub issues](https://img.shields.io/github/issues/iwatkot/maps4fsupgrader)](https://github.com/iwatkot/maps4fsupgrader/issues)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Build Status](https://github.com/iwatkot/maps4fsupgrader/actions/workflows/checks.yml/badge.svg)](https://github.com/iwatkot/maps4fsupgrader/actions)

</div>

# Maps4FS Upgrader

🔄 **Automated Docker Container Upgrader for Maps4FS Deployment**

A lightweight Docker container that automatically upgrades your Maps4FS deployment by pulling the latest images and redeploying containers


## Overview

The Maps4FS Upgrader is a containerized tool designed to simplify the upgrade process of your Maps4FS deployment. It automatically:

- 🛑 **Stops** running Maps4FS containers
- 🗑️ **Removes** old containers and images
- 📥 **Pulls** the latest Docker images
- 🚀 **Redeploys** containers with updated configurations
- ⏱️ **Handles** proper startup sequencing

## Supported Containers

The upgrader manages the following Maps4FS containers:
- **maps4fsapi** - The core API service
- **maps4fsui** - The web user interface

## Prerequisites

- Docker installed and running
- Existing Maps4FS deployment with containers named `maps4fsapi` and `maps4fsui`
- Access to Docker socket (`/var/run/docker.sock`)
- `USERPROFILE` environment variable set (for volume mounting)

## Usage

### Quick Upgrade

Run the upgrader with a single command:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e USERPROFILE="$HOME" \
  iwatkot/maps4fsupgrader
```

### Windows PowerShell

```powershell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -e USERPROFILE="$env:USERPROFILE" iwatkot/maps4fsupgrader
```

### What Happens During Upgrade

1. **Connects** to Docker daemon
2. **Stops** maps4fsapi container
3. **Removes** maps4fsapi container and image
4. **Pulls** latest maps4fsapi image
5. **Deploys** new maps4fsapi container
6. **Waits** 10 seconds for API to start
7. **Repeats** steps 2-5 for maps4fsui container
8. **Completes** with success confirmation

## Configuration

The upgrader uses predefined container configurations that match the standard Maps4FS deployment:

### Maps4FS API Container
- **Image**: `iwatkot/maps4fsapi`
- **Port**: `8000:8000`
- **Volumes**: Maps4FS data directories + Docker socket
- **Restart Policy**: `unless-stopped`

### Maps4FS UI Container
- **Image**: `iwatkot/maps4fsui`
- **Port**: `3000:3000`
- **Volumes**: Maps4FS data directories + Docker socket
- **Restart Policy**: `unless-stopped`

## Directory Structure

Expected Maps4FS directory structure:
```
$USERPROFILE/maps4fs/
├── mfsrootdir/     # Generated maps data
├── templates/      # Map templates
└── defaults/       # Default configurations
```

## Logging

The upgrader provides detailed logging for each step:
- Container status checks
- Image pulling progress
- Deployment confirmations
- Error handling and troubleshooting

## Error Handling

The upgrader includes robust error handling for:
- Docker daemon connection issues
- Missing containers or images
- Volume mounting problems
- Network connectivity issues

## Development

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/iwatkot/maps4fsupgrader.git
cd maps4fsupgrader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
python maps4fsupgrader/main.py
```

