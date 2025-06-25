# Toolbox.io — Web & Backend

Welcome to the Toolbox.io project! This repository contains the web frontend and backend for the Toolbox.io service. If you want to run the project locally, contribute, or just explore how it works, this guide will help you get started.

---

## 🚀 What is Toolbox.io?

Toolbox.io is a modern web application with a Python backend (FastAPI) and a frontend. It provides a secure, feature-rich environment for managing and protecting your data and applications. The backend is containerized using Docker and served via Caddy as a reverse proxy.

---

## 🖥️ Quick Start (Recommended)

The easiest way to run the project is with Docker. This ensures you have all dependencies and services running with a single command.

### 1. Install Docker

#### Linux/macOS
- Go to [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
- Download and follow the installation instructions for your OS.
- After installation, check Docker is working:
  ```sh
  docker --version
  ```

#### Windows
- Download Docker Desktop from [https://docs.docker.com/desktop/install/windows-install/](https://docs.docker.com/desktop/install/windows-install/)
- Run the installer and follow the prompts.
- After installation, check Docker is working:
  ```powershell
  docker --version
  ```

### 2. Clone the Repository
```sh
git clone https://github.com/Toolbox-io/site.git
cd Toolbox-io/Site
```

### 3. Start the Project
```sh
docker-compose up --build
```
- This will build and start all services (backend, frontend, Caddy proxy).
- The site will be available at [http://localhost:80](http://localhost:80) (or as configured in `docker-compose.yml`).

---

## 🌐 Frontend

The frontend is built from SCSS and TypeScript sources. It is **not static**—it requires a build step to generate the final HTML, CSS, and JS files.

- To build the frontend, run `npm run build` in the `frontend` directory.
- **Important:** Do NOT run the build outside Docker unless you know what you're doing, as HTML files will be overwritten.
- For development, you can edit the source files in `frontend/` and use Docker to handle the build process automatically.

---

## 🛠️ Useful Commands

- **Stop all Docker containers:**
  ```sh
  docker-compose down
  ```
- **Rebuild after code changes:**
  ```sh
  docker-compose up --build
  ```

---

## 📦 Project Structure

```
Site/
  backend/      # Python FastAPI backend
  frontend/     # Frontend source (HTML, SCSS, TypeScript, assets)
  caddy/        # Caddy reverse proxy config
  docker-compose.yml  # Multi-service orchestration
  Dockerfile    # Backend Docker build
```

---

## ❓ FAQ

- **Q: I get a port conflict error?**
  - A: Make sure nothing else is running on port 80 or 8000, or change the ports in `docker-compose.yml`.
- **Q: How do I update dependencies?**
  - A: For Python, update `requirements.txt` and run `pip install -r requirements.txt`.
- **Q: Where do I report bugs?**
  - A: Open an issue on [GitHub](https://github.com/Toolbox-io/Toolbox-io/issues).

---

Enjoy using Toolbox.io!