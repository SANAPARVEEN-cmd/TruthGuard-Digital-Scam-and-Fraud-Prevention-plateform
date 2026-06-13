# TruthGuard

**Verify Before You Trust**

TruthGuard is a production-quality academic Django project — a Digital Scam & Fraud Prevention Platform that helps users verify suspicious phone numbers, email addresses, and websites before becoming victims of fraud.

## Features

- **Entity Verification** — Search and analyze phone numbers, emails, and websites
- **Explainable Risk Scoring** — Transparent risk scores with human-readable explanations
- **Community Reporting** — Users can submit scam reports with evidence uploads
- **Fraud Alerts** — Filterable alert system for emerging threats
- **Threat Dashboard** — Chart.js-powered analytics with threat distribution and trends
- **Admin Panel** — Approve/reject reports, manage entities, alerts, and users
- **Security** — CSRF protection, rate limiting, secure file uploads, session security

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2+ |
| Database | SQLite (PostgreSQL-ready) |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |

## Quick Start

```bash
# Navigate to project
cd truthguard

# Activate virtual environment (if using venv)
# Windows:
..\venv\Scripts\activate
# macOS/Linux:
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed sample data
python manage.py seed_truthguard

# Create superuser (optional, seed creates admin/admin123)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** in your browser.

### Default Accounts (after seeding)

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |
| demo | demo123 | Regular user |

## Project Structure

```
truthguard/
├── manage.py
├── truthguard/          # Project settings
├── core/                # Home page, middleware, validators
├── accounts/            # Authentication & user profiles
├── entities/            # Entity search & verification
├── reports/             # Scam reporting
├── alerts/              # Fraud alerts
├── analytics/           # Patterns & risk engine
├── dashboard/           # Analytics dashboard
├── templates/           # HTML templates
├── static/              # CSS, JS, images
└── media/               # Uploaded evidence files
```

## Risk Scoring Engine

Located at `analytics/services/risk_engine.py`, the engine calculates scores based on:

- Approved community reports
- Reporter reputation scores
- Pattern signature matches
- Active alert associations
- Recent complaint surges

Every score returns an explanation list, e.g.:

> **82/100 — High Threat**
> - 15 approved community reports
> - Pattern match: Phishing URL Pattern
> - Recent complaint surge detected

## Future AI Modules (Architecture Ready)

The modular app structure supports future additions:

1. Scam Message Analyzer (`analytics/services/message_analyzer.py`)
2. URL Intelligence (`analytics/services/url_intelligence.py`)
3. Email Reputation Analysis (`analytics/services/email_reputation.py`)
4. Fraud Campaign Detection (`analytics/services/campaign_detection.py`)
5. AI Risk Prediction (`analytics/services/ai_prediction.py`)

## Color Palette

| Token | Hex |
|-------|-----|
| Primary | `#00E5FF` |
| Secondary | `#6C63FF` |
| Accent | `#00FFB2` |
| Background | `#0A0F1C` |
| Card | `#131B2E` |
| Danger | `#FF4D6D` |

## License

Academic project — TruthGuard © 2026
