# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an appointment scheduler system implementing both REST and GraphQL APIs to compare developer experience and API design patterns. Based on a system design interview scenario for healthcare appointment scheduling at enterprise scale (10k+ hospitals).

## Architecture

**Dual API Implementation:**
- **REST API**: FastAPI native endpoints with Pydantic models
- **GraphQL API**: Strawberry GraphQL with schema-first approach
- **Frontend**: Vue 3 + TypeScript with API switching capability
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Containerization**: Docker Compose for consistent development environment

## Development Commands

```bash
# Start entire application stack
docker-compose up

# Start with rebuild
docker-compose up --build

# Run backend only
docker-compose up backend db

# Access services
# Frontend: http://localhost:3000
# REST API docs: http://localhost:8000/docs
# GraphQL playground: http://localhost:8000/graphql
```

## Project Structure

```
appointment-scheduler/
├── docker-compose.yml
├── backend/app/
│   ├── main.py              # FastAPI app with both REST/GraphQL
│   ├── models/              # SQLAlchemy database models
│   ├── api/                 # API layer (REST + GraphQL)
│   │   ├── rest/           # FastAPI REST endpoints
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management (admin only)
│   │   │   ├── hospitals.py    # Hospital data endpoints
│   │   │   ├── appointments.py # Appointment CRUD
│   │   │   └── doctors.py      # Doctor availability management
│   │   └── graphql/        # Strawberry GraphQL schema
│   │       ├── auth.py         # Auth mutations/queries
│   │       ├── users.py        # User management schema
│   │       ├── hospitals.py    # Hospital data schema
│   │       ├── appointments.py # Appointment schema
│   │       └── doctors.py      # Doctor schema
│   └── core/               # Business logic and utilities
│       ├── auth.py             # JWT creation, password hashing
│       ├── security.py         # FastAPI auth dependencies
│       ├── permissions.py      # Role-based access control
│       ├── database.py         # Database connection
│       └── config.py           # Application configuration
├── frontend/src/           # Vue 3 + TypeScript
└── README.md              # System design analysis
```

## Core Data Models

**Person-Role Based Architecture:**

**Core Entities:**
- **Person**: Shared personal data (name, contact info) for all individuals
- **User**: Authentication and authorization for system access
- **Hospital**: Facility information with timezone and operating hours

**Role Entities:**
- **Doctor**: Medical professionals with specializations, licenses
- **Staff**: Administrative and support personnel with departments, titles
- **Patient**: Individuals receiving care with medical records, insurance

**Junction Tables:**
- **PersonRole**: Links persons to multiple roles (doctor + staff, etc.)
- **UserPerson**: Links authenticated users to person entities
- **Appointment**: Links doctors, patients, and time slots

**Benefits of This Architecture:**
- Multiple roles per person (doctor who handles admin duties)
- Clean separation of authentication from personal data
- Natural database constraints (only users can create appointments)
- Better security with role-based permissions
- Eliminates awkward boolean flags and constraint issues

## Key Design Decisions

**Consistency over Availability**: Strong consistency within hospital partitions to prevent double-booking, with optimistic locking for concurrent appointment creation.

**Appointment Storage Strategy**: Uses prepopulated appointment table approach rather than dynamic slot generation. Appointments are created as "available" slots (patient_id = NULL) when doctor sets availability, then updated to "booked" (patient_id assigned) when scheduled. This enables atomic booking operations, natural conflict resolution via database constraints, and efficient real-time updates via WebSocket/SSE.

**Doctor Availability Storage**: Doctor availability stored as JSONB for flexibility in setting complex schedules, but actual bookable slots exist as discrete appointment records.

**Timezone Handling**: Naive times + timezone stored separately to handle business rules and DST transitions correctly.

## Authentication Architecture

**JWT with httpOnly Cookies:**
- **Security**: Protects against XSS attacks (JavaScript cannot access httpOnly cookies)
- **Token Strategy**: Short-lived access tokens (15min) + long-lived refresh tokens (30 days)
- **Role-Based Access**: JWT payload contains user roles and hospital affiliations

**Core Authentication Components:**

**`app/core/auth.py`** - Pure Business Logic:
- `authenticate_user()` - Validate credentials against database
- `create_jwt_token()` - Generate access tokens with user context
- `create_refresh_token()` - Generate long-lived refresh tokens
- `verify_jwt_token()` - Decode and validate token signatures
- `hash_password()` / `verify_password()` - Secure password handling

**`app/core/security.py`** - FastAPI Dependencies:
- `get_current_user()` - Extract user from httpOnly cookie
- `require_admin()` - Admin-only endpoint protection
- `require_doctor_or_staff()` - Role-based access control
- `get_hospital_context()` - Hospital-scoped data access

**`app/core/permissions.py`** - Authorization Logic:
- Role validation and hospital affiliation checks
- Data filtering based on user permissions
- Appointment access control (doctors see only their appointments)

## API Comparison Focus

This implementation demonstrates:
- **REST**: Standard CRUD operations with clear HTTP semantics
- **GraphQL**: Flexible queries for complex calendar data fetching
- **Error Handling**: How each paradigm handles validation and conflicts
- **Developer Experience**: Code complexity and maintainability differences
- **Authentication**: Consistent security model across both API paradigms