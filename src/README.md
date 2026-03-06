# Mergington High School Activities API

A FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Unregister from activities
- Persist activities and registrations in SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Database and Migrations

The app uses a SQLite database at `src/mergington.db` by default.

- On startup, schema migrations are applied automatically.
- If the activities table is empty, seed data equivalent to the original in-memory sample is inserted.

Schema tables:

- `users`
- `activities`
- `registrations`
- `schema_migrations`

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All activity and registration data is stored in SQLite, so data is preserved across app restarts.

## Running Tests

From the repository root:

```
pytest
```
