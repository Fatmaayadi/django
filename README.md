# Plateforme de Gestion d'Événements (mini)

Ce projet est un squelette Django + Django REST Framework pour une plateforme de gestion d'événements.
Il contient un backend avec APIs et 3 pages frontend (HTML/CSS/vanilla JS) :
- Accueil (liste d'événements)
- Détail d'événement
- Inscription (avec choix d'intérêts)

## Installation rapide (local)
1. Crée un virtualenv et active-le.
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. Installe les dépendances:
   ```
   pip install -r requirements.txt
   ```
3. Make migrations & migrate:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Crée un superuser:
   ```
   python manage.py createsuperuser
   ```
5. Lance le serveur:
   ```
   python manage.py runserver
   ```
6. Ouvre `http://127.0.0.1:8000/`

## Notes
- DB par défaut: SQLite (pour dev). Tu peux changer dans `config/settings.py` pour PostgreSQL.
- Le paiement est simulé dans l'endpoint `/api/tickets/book/`. Un webhook demo existe dans `/api/payments/webhook/`.
- QR codes sont générés et sauvegardés dans `media/qrcodes/`.

## Fichiers importants
- `events/models.py` : modèles (User, Event, Ticket, Payment...)
- `events/views.py` : APIs principales
- `events/templates/` : pages HTML (3 pages)
- `events/static/css/style.css` : style minimal

Bonne continuation — adapte et améliore selon vos besoins d'équipe.
