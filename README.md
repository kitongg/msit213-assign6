# Photo Album Management (Django)

Production-ready Django Photo Album Management skeleton.

Key features:
- CBV-based CRUD for albums and photos
- Role-based access (Django auth: staff users are album admins)
- Cloudinary media storage ready
- PostgreSQL-ready settings via environment variables

Setup (local development):

1. Create virtualenv and install requirements

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` with required variables (see `photo_album/settings.py` for names)

3. Run migrations and create superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Deployment: intended for Render. Use environment variables for `SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_URL`, and set `DJANGO_SETTINGS_MODULE=photo_album.settings.production`.
