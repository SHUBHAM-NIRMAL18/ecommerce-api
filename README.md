# E‑Commerce API

[![Django](https://img.shields.io/badge/Django-5.2.4-green?logo=django&logoColor=white)](https://www.djangoproject.com/)  
[![DRF](https://img.shields.io/badge/Django--REST--Framework-3.16-blue?logo=django&logoColor=white)](https://www.django-rest-framework.org/)

This repository exposes a simple E‑Commerce API built with Django & Django REST Framework. It supports:

- **User & Roles**  
  - Register / Login (JWT)  
  - Two roles: **Admin** & **Customer**  
  - Only authenticated users can access any endpoint  

- **Category (Admin only writes)**  
  - List & Retrieve (any authenticated)  
  - Create / Update / Delete (Admin only)  

- **Product (Admin only writes)**  
  - List & Retrieve  
    - **Admin** sees all products  
    - **Customer** sees only active products  
  - Create / Update / Delete / Activate / Deactivate (Admin only)  

- **Order**  
  - **Customer**:  
    - Create order (quantity ≤ stock, product must be active)  
    - View own orders  
    - Cancel own order (only if status is `pending`)  
  - **Admin**:  
    - View all orders  
    - Change order status (`confirm`, `ship`, `deliver`, etc.)  

---



## Getting Started

1. **Clone & Install**

    Clone the repo
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. **Migrate and Run**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver

3. **API Documentaion**

    Swagger: 
    ```bash
    api/docs/
