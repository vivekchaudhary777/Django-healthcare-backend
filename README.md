# Healthcare Backend API

A Django REST Framework API for user registration, JWT authentication, patient records, doctor records, and patient-doctor assignments. Patient and mapping queries are scoped to the authenticated patient owner.

## Stack

- Python 3.10+
- Django 5.x and Django REST Framework
- SimpleJWT
- PostgreSQL in the Render configuration; SQLite is the local default

## Run locally

In PowerShell from the project directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set a private `SECRET_KEY`. For local development, keep `DEBUG=True` and `ALLOWED_HOSTS=localhost,127.0.0.1`. Generate a key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Without `DATABASE_URL`, the application uses `db.sqlite3`. For the verified local PostgreSQL setup, create a `healthcare_test` database and a login role named `healthcare_test`, then set `DATABASE_URL` in `.env` with that role's password:

```dotenv
DATABASE_URL=postgresql://healthcare_test:<URL_ENCODED_PASSWORD>@127.0.0.1:5432/healthcare_test
```

Replace the placeholder locally; URL-encode special characters in the password. Never put the real password in `.env.example` or source control.

Apply migrations and start the development server:

```powershell
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000`. `GET /api/health/` checks database connectivity. Never commit `.env` or real credentials.

## Authentication

Register at `POST /api/auth/register/`:

```json
{"name":"Alex Smith","email":"alex@example.com","password":"Use-a-strong-password-123"}
```

Login at `POST /api/auth/login/`:

```json
{"email":"alex@example.com","password":"Use-a-strong-password-123"}
```

Login returns `access` and `refresh` JWTs. Send the access token on protected requests as `Authorization: Bearer <access>`. Refresh at `POST /api/auth/token/refresh/` with `{"refresh":"<refresh-token>"}`. Access tokens last 15 minutes; refresh tokens last one day and rotate on use.

## API endpoints

All endpoints require a bearer token except registration, login, token refresh, and health. List responses are paginated.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register with name, email, and password |
| POST | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/auth/token/refresh/` | Rotate a refresh token |
| POST | `/api/patients/` | Create a patient owned by the current user |
| GET | `/api/patients/` | List the current user's patients |
| GET, PUT, DELETE | `/api/patients/<id>/` | Retrieve, update, or delete an owned patient |
| POST | `/api/doctors/` | Create a doctor; the creator controls updates and deletion |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/<id>/` | Retrieve any doctor |
| PUT, DELETE | `/api/doctors/<id>/` | Update or delete a doctor you created |
| POST | `/api/mappings/` | Assign a doctor to one of your patients |
| GET | `/api/mappings/` | List mappings for your patients |
| GET | `/api/mappings/<patient_id>/` | List doctors assigned to an owned patient |
| DELETE | `/api/mappings/<mapping_id>/` | Delete a mapping for an owned patient |
| GET | `/api/health/` | Check database connectivity |

The mapping detail route uses a patient ID for `GET` and a mapping ID for `DELETE`. A patient-doctor pair can only be assigned once. Cross-owner patient and mapping lookups return 404. Invalid input returns 400; missing or invalid authentication returns 401; attempts to delete an assigned doctor return 409.

Create a patient with `POST /api/patients/`:

```json
{"name":"Jordan Lee","date_of_birth":"1990-04-15","gender":"unspecified","email":"jordan@example.com","phone":"555-0100","address":"100 Main Street"}
```

Create a doctor with `POST /api/doctors/`:

```json
{"name":"Morgan Chen","specialization":"Cardiology","email":"morgan@example.com","phone":"555-0199","clinic_address":"10 Clinic Road"}
```

Assign that doctor to a patient with `POST /api/mappings/`:

```json
{"patient":1,"doctor":1}
```

Example authenticated request:

```powershell
curl.exe http://127.0.0.1:8000/api/patients/ -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Patient fields are name, date of birth, gender, email, phone, and address. Doctor fields are name, specialization, email, phone, and clinic address. IDs, ownership, and timestamps are managed by the server.

## Tests and checks

```powershell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

The local PostgreSQL configuration above was verified against database `healthcare_test`: migrations applied, `makemigrations --check --dry-run` reported no changes, and all 7 tests passed using Django's PostgreSQL test database. SQLite test results do not verify a PostgreSQL connection.

For a production configuration check, set `DEBUG=False`, a private `SECRET_KEY`, and the deployment host in `ALLOWED_HOSTS`, then run `python manage.py check --deploy`.

## Deployment configuration

`render.yaml` describes a Gunicorn web service and managed PostgreSQL database, with static collection and migrations before deployment. Review the provider's current plans and charges before creating services. This repository has not been deployed; no live URL or production database is verified.
