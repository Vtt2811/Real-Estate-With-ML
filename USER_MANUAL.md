# REAL ESTATE PROPERTY FINDER WITH ML - USER MANUAL

## 1. PROJECT OVERVIEW

The Real Estate Property Finder is a web application that helps people find, compare, and buy/sell properties. It uses artificial intelligence (Machine Learning) to predict property prices accurately. The system is designed for three types of users:

**For Buyers:** Search properties, view details, express interest, and get price predictions
**For Sellers:** List properties and manage inquiries from buyers
**For Administrators:** Manage users, approve properties, and monitor the platform

### Main Features:
- Search and filter thousands of properties
- View detailed property information with photos
- AI-powered price prediction for any property
- User registration and secure login
- Save favorite properties
- View buyer/seller profiles
- Admin panel for management

---

## 2. SYSTEM REQUIREMENTS

### What You Need to Install:
1. **Python 3.11** - Programming language (download from python.org)
2. **Git** - For downloading the project (download from git-scm.com)
3. **Any Web Browser** - Chrome, Firefox, Edge, or Safari for viewing the website
4. **Text Editor** - VS Code or Notepad++ (recommended)

### Minimum Computer Specifications:
- RAM: 4GB or more
- Storage: 2GB free space
- Internet: Required for installation and running
- OS: Windows, Mac, or Linux
---

## 3. HOW TO SET UP AND RUN THE PROJECT

### STEP 1: Install Python
- Download Python 3.11 from python.org
- During installation, CHECK the box that says "Add Python to PATH"
- Click Install

### STEP 2: Download the Project
Open Command Prompt (Windows) or Terminal (Mac/Linux) and type:
```
git clone https://github.com/yourusername/Real-Estate-With-ML-main.git
cd Real-Estate-With-ML-main
```

### STEP 3: Create Virtual Environment (Isolated Python Setup)
This keeps the project's libraries separate from your computer.

**Windows:**
```
python -m venv .venv
.\.venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
```

### STEP 4: Install Required Libraries
```
pip install -r requirements.txt
```
(This installs Django, Machine Learning tools, and other libraries needed)

### STEP 5: Setup Database
```
python manage.py migrate
```

### STEP 6: Create Admin Account
```
python manage.py createsuperuser
```
You will be asked to create:
- Username (e.g., admin)
- Email (e.g., admin@example.com)
- Password (enter a strong password twice)

### STEP 7: Add Sample Properties (Optional)
```
python manage.py load_properties
```

### STEP 8: Start the Server
**Option 1 (Windows):**
```
.\run_server.bat
```

**Option 2 (All Systems):**
```
python manage.py runserver
```

You will see:
```
Starting development server at http://127.0.0.1:8000/
```

### STEP 9: Open Website
Open your browser and go to: **http://127.0.0.1:8000/**

You now have the website running on your computer!

---

## 4. TECHNOLOGIES USED

### Backend (Server Side):
- **Django** - Web framework that handles all server logic
- **Python** - Programming language used for all code
- **SQLite** - Database to store all user and property information

### Frontend (What User Sees):
- **HTML** - Creates the structure of web pages
- **CSS** - Makes everything look beautiful with colors and layouts
- **JavaScript** - Adds interactive features like buttons and animations

### AI/Machine Learning:
- **scikit-learn** - Library for creating the price prediction model
- **pandas** - Tool for handling and organizing data
- **numpy** - Tool for mathematical calculations

---

## 5. HOW TO DEPLOY (Put Website Online)

### Option 1: Deploy on Heroku (Easiest for Beginners)

1. Create account on heroku.com
2. Install Heroku CLI from heroku.com/downloads
3. Open Command Prompt and go to your project folder
4. Run these commands:

```
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
```

Your website will be at: **your-app-name.herokuapp.com**

### Option 2: Deploy on AWS or DigitalOcean
- Create an account on aws.amazon.com or digitalocean.com
- Follow their guides for Python/Django deployment
- Point your domain name to the server

### Option 3: Use a Web Hosting Company
- Search for "Django hosting" online
- Many companies (like PythonAnywhere) make it very simple
- Just upload your project files

---

## 6. MAIN FEATURES WITH SCREENSHOTS DESCRIPTION

### Feature 1: HOME PAGE
**What you see:**
- Welcome message with a logo
- "Browse Properties" button
- "Sign In" and "Sign Up" buttons in top right
- Featured properties at bottom

**Purpose:** First page visitors see. They can decide to search properties or create an account.

---

### Feature 2: USER REGISTRATION (Sign Up)

**New User Signs Up:**
1. Clicks "Sign Up" button
2. Enters email address
3. Creates password
4. Selects user type (Buyer or Seller)
5. Clicks "Register"

**After Registration:**
- Account is created
- User is logged in automatically
- User is sent to their dashboard

---

### Feature 3: USER LOGIN (Sign In)

**Returning User Logs In:**
1. Clicks "Sign In" button
2. Enters email and password
3. Clicks "Login"
4. Taken to dashboard

**Features:**
- "Forgot Password" link to reset password
- Email verification (optional)

---

### Feature 4: BUYER DASHBOARD

**What Buyers See When They Log In:**

```
┌─────────────────────────────────────────────┐
│ WELCOME BACK, [USER NAME]!                  │
│ Explore properties and find your dream home │
└─────────────────────────────────────────────┘

STATISTICS:
├─ Total Properties: 100,000
├─ Matching Your Criteria: 50,000
├─ Cities Available: 5 (Gujarat)
└─ Property Types: Flat, House, Plot

AVAILABLE PROPERTIES:
├─ Property 1: "Plot in Vesu, Surat"
│  ├─ Area: 5000 sq ft
│  ├─ Price: ₹81.58 Lakh
│  ├─ Distance: 12.3 km from city
│  └─ [Show Interest Button]
│
├─ Property 2: "House in Mavdi, Rajkot"
│  ├─ Area: 1409 sq ft
│  ├─ Price: ₹1.13 Crore
│  ├─ Distance: 7.2 km from city
│  └─ [Show Interest Button]
└─ ... More properties ...

SIDEBAR MENU:
├─ 🏠 Browse Properties
├─ 📊 Price Predictions
├─ 👤 Profile
└─ 🚪 Sign Out
```

**What Users Can Do:**
- View all properties
- Click on any property to see full details
- Express interest in buying
- View their profile
- Check price predictions

---

### Feature 5: PROPERTY DETAILS PAGE

**When a Buyer Clicks on a Property:**

```
PROPERTY DETAILS:
├─ Large images showing the property
├─ Property name and location
├─ Specifications:
│  ├─ Bedrooms: 4
│  ├─ Bathrooms: 2
│  ├─ Area: 2,039 sqft
│  ├─ Price: ₹1.85 Crore
│  └─ Type: Flat/House/Plot
├─ Full description of the property
├─ Amenities (parking, gym, pool, etc.)
├─ Owner/Agent contact details
└─ [SHOW INTEREST Button]
```

**Features:**
- Gallery with multiple images
- Click images to see them larger
- All property details in one page
- Easy contact button

---

### Feature 6: AI PRICE PREDICTION

**What It Does:**
The system uses Machine Learning to predict the real market value of a property.

**How It Used to Show:**
```
PREDICT PRICE DROPDOWN:
├─ Estimated Price: ₹1,82,50,000
├─ Confidence: 98.6%
├─ Model considers:
│  ├─ Location (Sindhu Bhavan)
│  ├─ Area (2,039 sqft)
│  └─ Amenities
└─ Price Comparison:
   ├─ List Price: ₹1.85 Cr
   ├─ AI Estimate: ₹1.82 Cr
   └─ Area Average: ₹1.72 Cr
```

**NOTE:** This feature has been removed from the listing details page (as per your request).

---

### Feature 7: USER PROFILE

**Profile Shows:**
- User name and email
- Profile picture
- Contact information
- Email verification status
- Option to edit profile
- Option to change password
- History of interests shown

**User Can:**
- Update personal information
- Change password
- View profile picture
- See property interests/saved items

---

### Feature 8: ADMIN DASHBOARD

**Admin Can:**
- 👥 Manage all users (view, edit, delete)
- 🏘️ Approve new properties posted by sellers
- 📬 Verify buyer interests and inquiries
- 📈 View analytics and reports
- ⚙️ Change system settings

**Access:** http://127.0.0.1:8000/admin/
(Login with superuser account created in Step 6)

---

### Feature 9: SELLER DASHBOARD

**Sellers Can:**
- 📊 View overview of their properties
- ➕ Add new properties for sale
- 🏘️ Manage their listings
- 📬 See buyer inquiries and requests
- 👤 Update their profile

---

## 7. SIMPLE TROUBLESHOOTING GUIDE

### Problem 1: "Python is not recognized"
**Solution:** 
- Go to python.org and install Python again
- Make sure to CHECK "Add Python to PATH" during installation

### Problem 2: "ModuleNotFoundError: No module named 'django'"
**Solution:**
```
pip install -r requirements.txt
```

### Problem 3: "Port 8000 already in use"
**Solution:**
```
python manage.py runserver 8001
```
(Use port 8001 instead)

### Problem 4: Page shows "No such table" error
**Solution:**
```
python manage.py migrate
```

### Problem 5: Website doesn't load from http://127.0.0.1:8000/
**Solution:**
- Make sure server is running (you should see "Starting development server" message)
- Try refreshing the page with Ctrl+R (or Cmd+R on Mac)
- Clear browser cache (Ctrl+Shift+Delete)

### Problem 6: Login not working
**Solution:**
- Make sure you created a superuser with: `python manage.py createsuperuser`
- Check that you're using the correct email and password

---

## 8. QUICK REFERENCE COMMANDS

```
Activate environment (Windows):     .\.venv\Scripts\activate
Activate environment (Mac/Linux):   source .venv/bin/activate
Deactivate environment:             deactivate

Start server:                        python manage.py runserver
Create admin account:                python manage.py createsuperuser
Set up database:                     python manage.py migrate
Load sample data:                    python manage.py load_properties

Admin panel:                         http://127.0.0.1:8000/admin/
Main website:                        http://127.0.0.1:8000/
```

---

## 9. FILE STRUCTURE (What Each Folder Contains)

```
Real-Estate-With-ML-main/
│
├─ manage.py                    File to run commands
├─ db.sqlite3                   Database (stores all data)
├─ requirements.txt             List of libraries to install
├─ run_server.bat               Script to start server (Windows)
│
├─ realestate/                  Main project folder
│  ├─ settings.py               Configuration file
│  ├─ urls.py                   Website routes
│  └─ wsgi.py                   Server file
│
├─ listings/                    Main app folder
│  ├─ models.py                 Database structure
│  ├─ views.py                  Main logic
│  ├─ urls.py                   App routes
│  └─ forms.py                  User forms
│
├─ templates/                   HTML web pages
│  ├─ index.html                Home page
│  ├─ signin.html               Login page
│  ├─ signup.html               Registration page
│  ├─ profile.html              User profile
│  ├─ listing-details.html      Property details
│  └─ dashboards/               User dashboards
│
├─ static/                      Images and styling
│  ├─ css/                      Stylesheets
│  ├─ js/                       JavaScript files
│  └─ images/                   Pictures
│
└─ USER_MANUAL.md              This file
```

---

## 10. PROJECT INFORMATION

**Project Name:** Real Estate Property Finder with Machine Learning
**Purpose:** To help people find properties and predict accurate prices using AI
**Built With:** Django, Python, JavaScript, HTML, CSS
**Database:** SQLite (for development), PostgreSQL (for production)
**Version:** 1.0.0
**Date:** March 2026

---

## SUMMARY

This project is a complete real estate website where:
1. Users can register and log in
2. Buyers can search and view properties
3. AI predicts property prices
4. Sellers can list properties
5. Admins manage the platform

The setup is straightforward - just follow the 9 steps in Section 3, and you'll have a working website on your computer!

