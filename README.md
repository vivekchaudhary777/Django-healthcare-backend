# Healthcare Backend API

A Django REST Framework API for account registration and JWT login, user-owned patient records, shared doctor discovery, and patient-doctor assignments. The PDF assignment's listed routes are implemented. PostgreSQL is the production database; SQLite is the zero-setup local default.

## Architecture and data policy

- `accounts`: email-based custom user model, registration, login, JWTs.
- `patients`: records belong to their creator; list and object querysets are scoped to that owner.
- `doctors`: every authenticated user can list and retrieve every doctor. Only the creating user can update or delete a doctor. A doctor assigned to any patient cannot be deleted (HTTP 409).
- `mappings`: assignment rows belong to the patient owner, are unique by patient and doctor, and protect doctors from deletion while assigned.
- `config`: environment-based settings, URLs, database health endpoint, WSGI/ASGI.

Patient fields: `name` (required), `date_of_birth` (optional, cannot be in the future), `gender` (`female`, `male`, `other`, `unspecified`), `email`, `phone`, and `address`. Doctor fields: `name`, `specialization` (required), `email`, `phone`, `clinic_address`. IDs and timestamps are server-managed.

## Requirements

- Python 3.10+
- PostgreSQL 14+ for a PostgreSQL-backed local setup or deployment
- Git (optional for local use)

## Local setup

PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The supplied `.env.example` uses SQLite. To use PostgreSQL, create a database and replace `DATABASE_URL` in `.env` with a PostgreSQL URL, for example:

```dotenv
DATABASE_URL=postgresql://healthcare:your-password@localhost:5432/healthcare
```

Set a private random `SECRET_KEY` and `DEBUG=False` for production. `ALLOWED_HOSTS` is a comma-separated list. The application loads `.env` for local development; never commit it.

Initialize and run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is at `http://127.0.0.1:8000`. Health check: `GET /api/health/` returns `{"status":"ok","database":"connected"}` when the database is reachable.

## Authentication

Register with `POST /api/auth/register/`:

```json
{"name":"Alex Smith","email":"alex@example.com","password":"Use-a-strong-password-123"}
```

Success is HTTP 201 with user ID, name and normalized email; the password is never returned. Passwords must meet Django's configured validators.

Login with `POST /api/auth/login/`:

```json
{"email":"alex@example.com","password":"Use-a-strong-password-123"}
```

Success (HTTP 200): `{"access":"<JWT>","refresh":"<JWT>"}`. Access tokens last 15 minutes and refresh tokens one day. Refresh at `POST /api/auth/token/refresh/` with `{"refresh":"<JWT>"}`. Send the access token on protected requests as `Authorization: Bearer <access>`.

## Endpoints

All endpoints below except registration, login, token refresh, and health require a valid bearer token. Lists are page-number paginated (50 results per page), returning `count`, `next`, `previous`, and `results`.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/auth/register/` | Create account |
| POST | `/api/auth/login/` | Get access and refresh JWTs |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/patients/` | Create own patient |
| GET | `/api/patients/` | List own patients |
| GET / PUT / DELETE | `/api/patients/<id>/` | Read, replace, or delete own patient |
| POST | `/api/doctors/` | Create doctor; creator owns write access |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/<id>/` | Retrieve any doctor |
| PUT / DELETE | `/api/doctors/<id>/` | Update/delete only a doctor you created |
| POST | `/api/mappings/` | Assign doctor to own patient |
| GET | `/api/mappings/` | List assignments for own patients |
| GET | `/api/mappings/<patient_id>/` | List doctors assigned to that owned patient |
| DELETE | `/api/mappings/<mapping_id>/` | Delete an assignment belonging to own patient |
| GET | `/api/health/` | Database connectivity health check |

The mapping detail route uses its integer as a **patient ID for GET** and a **mapping ID for DELETE**, as specified by the assignment. The two operations are distinguished by HTTP method.

Create a patient:

```json
{"name":"Jordan Lee","date_of_birth":"1990-04-15","gender":"unspecified","email":"jordan@example.com","phone":"555-0100","address":"100 Main Street"}
```

Create a doctor:

```json
{"name":"Morgan Chen","specialization":"Cardiology","email":"morgan@example.com","phone":"555-0199","clinic_address":"10 Clinic Road"}
```

Create an assignment:

```json
{"patient":1,"doctor":1}
```

An assignment response has `id`, `patient`, `doctor`, and `created_at`. Duplicate patient-doctor pairs return HTTP 400. Cross-owner patient/mapping access returns 404 so record existence is not disclosed. Missing resources return 404, invalid fields return 400, missing/invalid authentication returns 401, and deletion of an assigned doctor returns 409.

Example using curl:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H 'Content-Type: application/json' \
  -d '{"email":"alex@example.com","password":"Use-a-strong-password-123"}'

curl http://127.0.0.1:8000/api/patients/ \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

The same requests can be imported into Postman or run with curl. JSON validation errors use DRF's field-keyed format, for example `{"name":["This field is required."]}`.

## Tests and checks

```powershell
python manage.py test
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
```

Tests cover registration, case-insensitive duplicates, login, token-protected access, patient CRUD/isolation, doctor CRUD/permissions, mapping creation/list/retrieval/deletion, duplicate and invalid references, health, and doctor deletion protection. Configure a PostgreSQL `DATABASE_URL` before tests to exercise them against PostgreSQL; the default test database otherwise uses SQLite.

## Deployment (Render blueprint)

`render.yaml` defines a Gunicorn web service, managed PostgreSQL, generated secret, HTTPS redirect, static collection, and a pre-deploy migration. Review the blueprint's current pricing and service availability before provisioning; the configuration is prepared, but this workspace has no Render account credentials or deployment access, so no hosted service or URL is claimed. Set `ALLOWED_HOSTS` to the actual service hostname if it changes. Configure environment variables in the provider dashboard, never in source control.

The API's production database is PostgreSQL when `DATABASE_URL` is supplied. Production startup requires `DEBUG=False`, a strong `SECRET_KEY`, and the correct `ALLOWED_HOSTS`. Health monitoring should use `/api/health/`.

## Repository status and limitations

The source directory initially had no Git repository or remote configured and the GitHub CLI was not installed. This local implementation therefore does not claim a commit or publication. Publishing requires an authenticated GitHub repository and remote. No live deployment, PostgreSQL server, or production API has been configured or verified in this environment.
