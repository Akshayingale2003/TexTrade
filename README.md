"# TexTrade" 

TexTrade – Textile Selling Web Application

TexTrade is a modern web-based platform built using Django that allows users to browse, purchase, and manage textile products, while vendors can list and manage their inventory. The platform also includes a smart FAQ-based chatbot for customer support.

Features
-User Features
User Registration & Login Authentication
Browse textile categories (Cotton, Silk, etc.)
Add products to cart
Place orders securely
Track order status
Chatbot support for instant queries
-Vendor Features
Vendor registration & login
Add, update, delete products
Manage product categories
View customer orders
-Admin Features
Full control over users and vendors
Manage products and categories
Manage FAQ chatbot questions & answers
Activate/Deactivate FAQs
-Chatbot System
FAQ-based automated response system
Admin-controlled questionnaire
Instant replies to user queries

Tech Stack
Backend: Django (Python)
Frontend: HTML, CSS, JavaScript
Database: SQLite 
Authentication: Django Auth System


Installation & Setup

1️. Clone the Repository - 
git clone https://github.com/your-username/textrade.git
cd textrade

2️. Create Virtual Environment - 
python -m venv venv
venv\Scripts\activate  

3️. Install Dependencies - 
pip install -r requirements.txt

4️. Apply Migrations - 
python manage.py makemigrations

5. migrate migrations - 
python manage.py migrate

6. Create Superuser - 
python manage.py createsuperuser

7. Run Server - 
python manage.py runserver