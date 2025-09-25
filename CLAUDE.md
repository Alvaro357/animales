# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based web application for animal adoption associations management system with Tailwind CSS for styling. The system allows associations to register, manage animals for adoption, and includes an admin approval workflow with Telegram notifications.

## Development Commands

### Django Server & Management
```bash
# Run development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for Django admin
python manage.py createsuperuser

# Populate database with sample animals (custom command)
python manage.py poblar_animales

# Collect static files (production)
python manage.py collectstatic
```

### Frontend Development
```bash
# Install npm dependencies (Tailwind CSS)
npm install

# Build CSS with Tailwind (if using Tailwind standalone)
npx tailwindcss build
```

### Testing
```bash
# Run Django tests
python manage.py test

# Run specific app tests
python manage.py test myapp
```

## Architecture Overview

### Core Structure
- **Django Project**: `mysite/` - Main project configuration
- **Main Application**: `myapp/` - Contains all business logic for animal associations
- **Database**: SQLite3 for development, configurable for production
- **Static Files**: Managed by WhiteNoise in production
- **Media Files**: Stored in `media/` directory for animal photos and association logos

### Key Models (myapp/models.py)
1. **RegistroAsociacion**: Animal associations with approval workflow
   - States: pendiente, activa, suspendida, rechazada, eliminada
   - Token-based management system for admin actions
   - Integration with Telegram notifications

2. **CreacionAnimales**: Animals available for adoption
   - Linked to associations via ForeignKey
   - Includes adoption status tracking
   - Supports images and videos

3. **AnimalFavorito**: Tracks user favorites by IP address

### URL Structure (myapp/urls.py)
- Public pages: `/`, `/registro/`, `/login/`, `/buscador-avanzado/`
- Association management: `/mis_animales/`, `/crear_animal/`
- Admin panel: `/admin/panel/` with token-based approval system
- Telegram webhook: `/telegram/webhook/`

### Authentication & Session Management
- Custom session-based authentication for associations
- Token-based admin actions (approval/rejection via email links)
- Session cookies with 24-hour expiration
- Custom decorator: `@session_login_required`

### External Integrations
- **Telegram Bot**: Real-time notifications for admin actions
  - Bot token and chat ID configured in `telegram_utils.py`
  - Webhook endpoint for interactive responses
- **Email System**: SMTP configuration for notifications
  - Uses iCloud mail (configured in settings.py)

### Frontend Stack
- **Tailwind CSS**: For styling (v4.1.3)
- **Django Templates**: Server-side rendering
- **django-browser-reload**: Hot reload in development

## Important Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key (defaults to development key if not set)
- `DEBUG`: Set to False in production
- `RENDER_EXTERNAL_HOSTNAME`: For Render.com deployment

### ALLOWED_HOSTS
Currently configured for localhost, ngrok tunnels, and Render deployment

### Media Files
- Upload directories: `media/Fotos/` for images, `media/videos/` for videos
- Served directly in development, requires proper configuration in production

## Development Notes

### Migration Status
The project has pending migrations that need to be consolidated. Several migration files have been deleted but changes are uncommitted.

### Custom Management Commands
- `poblar_animales`: Creates 500 sample animals distributed across associations (40% dogs, 35% cats, 25% others)

### Template System
All templates are in `myapp/templates/` with extensive use of Tailwind classes for styling. Key templates:
- `index.html`: Main landing page
- `admin_panel.html`: Administrative dashboard
- `mis_animales.html`: Association's animal management
- `buscador_avanzado.html`: Advanced search functionality

### Security Considerations
- CSRF protection enabled
- Password hashing for association accounts
- Token-based secure links for admin actions
- Trusted origins configured for ngrok tunnels