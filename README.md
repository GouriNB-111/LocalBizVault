# 🏪 LocalBizVault

A cloud-based e-commerce platform that empowers local businesses to create and manage their own online storefronts — built with Flask and deployed on Render.

## 🚀 Live Demo
[https://localbizvault.onrender.com](https://localbizvault.onrender.com)

## 📌 Features

- 🏬 **Multi-shop platform** — shopkeepers get their own storefront at `/shop-slug`
- 🛒 **Customer shopping** — browse shops, add to cart, checkout
- 💳 **Dual payment** — Cash on Delivery & UPI/QR Pay with UTR verification
- 📦 **Order management** — shopkeepers manage orders and payment status
- 🚀 **Store deployment** — shopkeepers deploy their store live with one click
- 🔐 **Role-based auth** — separate flows for customers and shopkeepers

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | PostgreSQL (Render) / SQLite (local) |
| ORM | Flask-SQLAlchemy, Flask-Migrate |
| Auth | Flask-Login |
| Frontend | Jinja2, Bootstrap 5, Custom CSS |
| Deployment | Render (PaaS) |

## ⚙️ Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/GouriNB-111/LocalBizVault.git
cd LocalBizVault

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 5. Run database migrations
flask db upgrade

# 6. Start the app
flask run
```

## 🌍 Deployment

This app is deployed on **Render** using `render.yaml` (Blueprint deploy).

It uses:
- Render **Web Service** for the Flask app
- Render **PostgreSQL** (free tier) for the database
- Auto-runs `flask db upgrade` on every deploy

## 📁 Project Structure

```
LocalBizVault/
├── app/
│   ├── __init__.py         # App factory
│   ├── models.py           # Database models
│   ├── routes.py           # All routes
│   ├── forms.py            # WTForms
│   ├── utils.py            # Helper functions
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── admin/          # Shopkeeper views
│       │   ├── dashboard.html
│       │   ├── orders.html
│       │   ├── add_product.html
│       │   ├── store_status.html
│       │   ├── login.html
│       │   └── register.html
│       └── storefront/     # Customer views
│           ├── storefront.html
│           ├── cart.html
│           └── checkout.html
├── migrations/             # Flask-Migrate files
├── config.py               # App configuration
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── Procfile                # Process file for deployment
└── run.py                  # App entry point
```

## 👤 User Roles

**Shopkeeper**
- Register → add products → deploy store → manage orders

**Customer**
- Browse live shops → add to cart → checkout → pay via COD or UPI

## ☁️ Cloud Computing Concepts Applied

- **PaaS** (Platform as a Service) — Render hosts the app without server management
- **DBaaS** (Database as a Service) — Managed PostgreSQL on Render
- **Auto-scaling** — Render handles traffic scaling automatically
- **CI/CD** — Auto-deploys on every GitHub push
- **Environment variables** — Secrets managed securely via Render dashboard
