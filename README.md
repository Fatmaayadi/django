

---

# **Event Management Platform **

This project is a **Django + Django REST Framework** skeleton for a simple event management platform.
It includes a backend with APIs and three frontend pages built with **HTML/CSS/vanilla JavaScript**:

* **Home** – Displays the list of events
* **Event Details** – Shows information about a specific event
* **Registration** – Allows users to register and select their interests

---

## **Quick Installation (Local)**

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create and apply migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**

   ```bash
   python manage.py runserver
   ```

6. Open your browser at:
   **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## **Notes**

* Default database: **SQLite** (for development).
  You can switch to **PostgreSQL** in `config/settings.py`.
* Payment is simulated via the endpoint:
  `/api/tickets/book/`
* A demo webhook is available at:
  `/api/payments/webhook/`
* QR codes are generated and stored in:
  `media/qrcodes/`

---

## **Key Files**

* `events/models.py` — Models (User, Event, Ticket, Payment, etc.)
* `events/views.py` — Main API views
* `events/templates/` — HTML pages (3 pages)
* `events/static/css/style.css` — Minimal styling

---

