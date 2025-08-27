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
│   ├── models/              # SQLAlchemy models
│   ├── api/
│   │   ├── rest/           # FastAPI REST endpoints
│   │   └── graphql/        # Strawberry GraphQL schema
│   └── core/               # Database, auth, config
├── frontend/src/           # Vue 3 + TypeScript
└── README.md              # System design analysis
```

## Core Data Models

Based on system design analysis in README.md:

- **Hospital**: Contains timezone, operating hours, and location data
- **Doctor**: Linked to single hospital, has availability stored as JSONB
- **Patient**: Basic patient information
- **Appointment**: Links doctor, patient, and time slot with concurrency controls

## Key Design Decisions

**Consistency over Availability**: Strong consistency within hospital partitions to prevent double-booking, with optimistic locking for concurrent appointment creation.

**Appointment Storage Strategy**: Uses prepopulated appointment table approach rather than dynamic slot generation. Appointments are created as "available" slots (patient_id = NULL) when doctor sets availability, then updated to "booked" (patient_id assigned) when scheduled. This enables atomic booking operations, natural conflict resolution via database constraints, and efficient real-time updates via WebSocket/SSE.

**Doctor Availability Storage**: Doctor availability stored as JSONB for flexibility in setting complex schedules, but actual bookable slots exist as discrete appointment records.

**Timezone Handling**: Naive times + timezone stored separately to handle business rules and DST transitions correctly.

## API Comparison Focus

This implementation demonstrates:
- **REST**: Standard CRUD operations with clear HTTP semantics
- **GraphQL**: Flexible queries for complex calendar data fetching
- **Error Handling**: How each paradigm handles validation and conflicts
- **Developer Experience**: Code complexity and maintainability differences