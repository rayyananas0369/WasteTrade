
# ♻️ WasteTrade — Community Waste-to-Value Platform

WasteTrade is a web-based recycling marketplace that connects households and other waste generators with local scrap dealers.

The platform helps customers list recyclable materials, view estimated prices, and request waste pickups. Verified dealers can accept available requests and arrange collections.

> **Project Status:** 🚧 Under Active Development

## 🎯 Project Objectives

- Make recyclable waste collection simple and accessible.
- Connect customers with verified local scrap dealers.
- Provide transparent estimated waste prices.
- Support multiple waste items in a single pickup request.
- Improve recycling efficiency through digital pickup management.
- Encourage sustainable waste disposal.

## ✨ Features

### 👤 Customer Module

- Customer registration and secure login
- Customer dashboard
- Add recyclable waste items
- Multiple-item waste basket
- Edit and remove basket items
- Admin-managed reference waste prices
- Condition-based estimated pricing
- Submit pickup requests
- View submitted listings and request status
- View scheduled pickup details

### 🚚 Dealer Module

- Dealer registration
- Admin approval before dealer access
- Dealer dashboard
- View available requests in the service area
- Accept customer waste listings
- View accepted pickups
- Schedule pickup date and time

### 🛡️ Administration

- Django Admin for platform management
- Manage registered users
- Approve dealer accounts
- Set waste prices per kilogram
- Monitor waste listings
- WasteTrade-themed administration interface

## 💰 Estimated Price Calculation

WasteTrade calculates estimated prices using an administrator-defined base rate and waste condition.

| Waste Condition | Rate Applied |
|-----------------|--------------|
| Clean / Dry | 100% |
| Mixed | 80% |
| Damaged / Used | 60% |

**Formula:**

Estimated Amount = Estimated Weight × Base Rate × Condition Multiplier

Example:

- Waste type: Old Books
- Estimated weight: 10 kg
- Base price: ₹8/kg
- Condition: Mixed
- Condition multiplier: 0.80

Estimated Amount = 10 × 8 × 0.80 = **₹64**

These rates are for demonstration purposes and do not represent real-time market prices.

Final payment may differ based on actual weight and condition at pickup.

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, Django 5.2 |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite |
| Authentication | Django Authentication |
| Administration | Django Admin |
| Image Processing Support | Pillow |
| Version Control | Git and GitHub |

## 📁 Project Structure

```text
WasteTrade/
├── backend/
│   ├── config/
│   ├── core/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   └── manage.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   └── templates/
│       ├── accounts/
│       ├── core/
│       ├── customer/
│       ├── dealer/
│       └── admin/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/WasteTrade.git
cd WasteTrade
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
```

### 3. Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

Example:

```env
DJANGO_SECRET_KEY=your-generated-django-secret-key
DJANGO_DEBUG=True
```

Do not commit the `.env` file to GitHub.

### 5. Apply Database Migrations

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 6. Create an Administrator Account

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

### 7. Run the Development Server

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open:

- Website: http://127.0.0.1:8000/
- Signup: http://127.0.0.1:8000/signup/
- Login: http://127.0.0.1:8000/login/
- Django Admin: http://127.0.0.1:8000/admin/

After creating an administrator account, add active reference prices under **Waste Rates** in Django Admin before testing the Add Waste feature.

## 🔐 Security Features

- Django password hashing
- CSRF protection for forms
- User authentication and sessions
- Customer, Dealer, Collector, and Admin role definitions
- Dealer approval requirement
- Role-based view restrictions
- Customer ownership checks for waste listings
- Environment-variable-based secret configuration

## 🔄 Development Roadmap

- [x] Home page and responsive frontend
- [x] Customer and dealer registration
- [x] Login and logout
- [x] Customer dashboard
- [x] Waste rate management
- [x] Add Waste and multiple-item basket
- [x] Condition-based estimated pricing
- [x] Waste pickup request submission
- [x] My Listings
- [x] Dealer waste acceptance
- [x] Pickup scheduling implementation
- [ ] Full collector account management
- [ ] Collector dashboard
- [ ] Actual waste weight verification
- [ ] Customer final amount confirmation
- [ ] Offline payment record management
- [ ] Reports and analytics
- [ ] End-to-end testing and deployment

**Note:** Checked items indicate features implemented in the codebase. Full end-to-end testing is ongoing.

## 💳 Payments

WasteTrade does not currently integrate an online payment gateway.

The planned payment process supports offline transactions, such as cash or UPI, after collection and verification.

## 🌱 Project Vision

WasteTrade aims to turn recyclable waste into economic value while making the recycling process transparent, convenient, and accessible.

---

**Developed as a personal web development project.**

*Turn Waste Into Value.*
