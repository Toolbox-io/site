# Toolbox.io

A comprehensive security application for Android devices with a full-stack web platform for user management and support.

## 🚀 Features

### Android App
- **App Locking**: Protect apps with fake crash messages
- **Unlock Protection**: Alarm and photo capture on failed unlock attempts
- **Touch Protection**: Detect unauthorized physical access
- **Quick Settings Tiles**: Sleep mode and other utilities
- **App Manager**: Share APKs, manage apps, and more
- **Shortcuts**: Access to hidden system apps

### Web Platform
- **User Authentication**: JWT-based secure login system
- **Photo Storage**: Encrypted photo backup and sync
- **Support Chat**: AI-powered support system
- **Issue Reporting**: GitHub integration for bug reports
- **API Documentation**: Comprehensive REST API

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **MySQL** - Database
- **JWT** - Authentication
- **bcrypt** - Password hashing
- **Rate Limiting** - API protection

### Frontend
- **TypeScript** - Type-safe JavaScript
- **SCSS** - Styled components
- **Material Design** - Modern UI components
- **WebSocket** - Live reload (development)

### Android
- **Kotlin** - Modern Android development
- **Jetpack Compose** - Modern UI toolkit
- **Material 3** - Latest design system

## 📋 Prerequisites

### For Local Development (No Docker)
- **Node.js 18+** - For frontend development
- **Python 3.9+** - For backend development
- **SQLite** - Built-in database (no installation needed)

### For Production Deployment
- **Docker & Docker Compose** - For easy deployment
- **MySQL 8+** - Database
- **Android Studio** - For Android development

## 🚀 Quick Start

### Local Development (No Docker)

#### 1. Clone the Repository
```bash
git clone https://github.com/Toolbox-io/site.git
cd site
```

#### 2. Install Dependencies
```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend/main && pip install -r requirements.txt && cd ../..
```

#### 3. Environment Setup
```bash
# Copy the environment template (works for both dev and prod)
cp env.example .env

# Edit .env with your values (optional - defaults work for basic development)
# Set ENV=development for SQLite, ENV=production for MySQL
nano .env
```

#### 4. Start Development Services
```bash
# Start all services at once
npm run development:all

# Or start individual services:
# npm run development:backend     # Unified backend (API + Download + Support Bot)
# npm run development:frontend   # Frontend with hot reload
```

#### 5. Access the Application
- **Web App**: http://localhost:8000
- **Download Service**: http://localhost:8000/download/
- **Database**: SQLite file at `backend/main/data/toolbox_dev.db`

### Production Deployment (Docker)

#### 1. Clone the Repository
```bash
git clone https://github.com/Toolbox-io/site.git
```

#### 2. Environment Setup
```bash
# Copy the environment template (same file for dev and prod)
cp env.example .env

# Edit .env with your actual values
# Set ENV=production for Docker deployment
nano .env
```

#### 3. Start with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 4. Access the Application
- **Web App**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs (if enabled)
- **Download Service**: http://localhost:8000/download/

## 🔧 Development Setup

### Using VSCode Tasks
The project includes VSCode tasks for easy development:

1. **Run** - Starts unified backend + frontend (TypeScript + SCSS watch)
2. **Development** - Starts all services (unified backend + frontend)
3. **Backend** - Just the unified backend (API + Download + Support Bot)
4. **TypeScript: Watch** - Frontend TypeScript compilation
5. **SCSS: Watch** - Frontend SCSS compilation

### Manual Development

#### Backend Development
```bash
cd backend/main
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp ../../env.development.example .env
# Edit .env with your values

# Run the server
ENV=development python main.py
```

#### Frontend Development
```bash
cd frontend
npm install
npm run build  # Compile TypeScript to JavaScript
npm run watch:ts  # Watch TypeScript changes
npm run watch:scss  # Watch SCSS changes
```

### Android Development
```bash
cd ../Android
./gradlew assembleDebug
```

## 📁 Project Structure

```
Toolbox.io/
├── Site/                    # Web platform
│   ├── backend/
│   │   └── main/           # Unified backend (API + Download + Support Bot)
│   ├── frontend/           # Web frontend
│   ├── caddy/              # Reverse proxy
│   └── docker-compose.yml  # Docker configuration
├── Android/                # Android application
│   ├── app/                # Main app module
│   ├── androidUtils/       # Utility library
│   └── utils/              # Common utilities
└── Support Bot/            # Standalone support bot
```

## 🔐 Environment Variables

See `env.example` for all required environment variables:

### Required Variables
- `SECRET_KEY` - JWT signing key (minimum 32 characters)
- `DB_PASSWORD` - Database password
- `SMTP_PASSWORD` - Email service password

### Optional Variables
- `OPENAI_API_KEY` - For AI support chat
- `TELEGRAM_BOT_TOKEN` - For Telegram bot
- `GITHUB_*` - For issue reporting integration

## 🚀 Deployment

### Production Deployment
1. Set up a server with Docker
2. Configure environment variables
3. Set up SSL certificates
4. Update Caddy configuration
5. Run `docker-compose -f docker-compose.yml --profile prod up -d`

### Database Setup
The application will automatically create the database schema on first run.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Bug Reports

Found a bug? Please report it:
- **GitHub Issues**: [Create an issue](https://github.com/your-username/Toolbox.io/issues/new)
- **Email**: support@toolbox-io.ru

## 🔒 Security

Found a security vulnerability? Please report it responsibly:
- **Email**: support@toolbox-io.ru
- **GitHub Security**: Use GitHub's private vulnerability reporting

## 🙏 Acknowledgments

- Material Design for UI components
- FastAPI for the excellent Python framework
- Jetpack Compose for modern Android development

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/your-username/Toolbox.io/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/Toolbox.io/issues)
- **Email**: support@toolbox-io.ru
- **Website**: https://toolbox-io.ru

---

**Made with ❤️ for Android security**
