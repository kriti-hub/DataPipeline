# WellNow Staffing Analytics -- Simulated HRIS REST API Specification

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Patterns](#common-response-patterns)
4. [Endpoints](#endpoints)
   - [GET /health](#get-health)
   - [GET /api/v1/workers](#get-apiv1workers)
   - [GET /api/v1/workers/{employee_id}](#get-apiv1workersemployee_id)
   - [GET /api/v1/schedules](#get-apiv1schedules)
   - [GET /api/v1/patient-volume](#get-apiv1patient-volume)
   - [GET /api/v1/locations](#get-apiv1locations)
   - [GET /api/v1/terminations](#get-apiv1terminations)
5. [Pagination Specification](#pagination-specification)
6. [Error Response Format](#error-response-format)
7. [Rate Limiting](#rate-limiting)
8. [Data Generation Notes](#data-generation-notes)

---

## Overview

This document specifies the Simulated HRIS REST API, a FastAPI application that generates realistic workforce and operational data for the WellNow Staffing Analytics pipeline. The API simulates three upstream data systems:

- **HRIS (Human Resources Information System)** -- Employee demographics, roles, and termination records.
- **Scheduling System** -- Scheduled and actual shift data for all staff.
- **Patient Volume System** -- Daily patient visit counts, wait times, and visit-type breakdowns.

The API serves as the ingestion source for the Bronze layer of the Medallion architecture.

**Base URL:** Configurable via the `HRIS_API_URL` environment variable (e.g., `http://localhost:8000`).

**Framework:** FastAPI (Python)

**Content Type:** All responses are `application/json`.

---

## Authentication

All endpoints except `/health` require authentication via an API key passed in the request header.

| Header       | Value                        |
|--------------|------------------------------|
| `X-API-Key`  | Value of `HRIS_API_KEY` env var |

**Configuration:**

The API key is set through the `HRIS_API_KEY` environment variable on the server. Clients must include the matching key in every request to protected endpoints.

**Unauthorized Response (401):**

If the `X-API-Key` header is missing or does not match the configured key, the API returns:

```json
{
  "error": {
    "code": 401,
    "message": "Unauthorized",
    "details": "Missing or invalid API key. Provide a valid X-API-Key header."
  }
}
```

---

## Common Response Patterns

### Paginated Response Envelope

All paginated endpoints return data in the following structure:

```json
{
  "data": [
    { "...record..." },
    { "...record..." }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_records": 1200,
    "total_pages": 12
  }
}
```

### Error Response Envelope

All error responses use a consistent structure:

```json
{
  "error": {
    "code": 400,
    "message": "Bad Request",
    "details": "Description of what went wrong."
  }
}
```

### Date and Timestamp Formats

- **Dates** are formatted in ISO 8601: `YYYY-MM-DD` (e.g., `2024-06-15`).
- **Timestamps** are formatted in ISO 8601 with timezone: `YYYY-MM-DDTHH:MM:SS+00:00` (e.g., `2024-06-15T08:30:00+00:00`).

---

## Endpoints

---

### GET /health

Health check endpoint. Returns the service status, version, and current server timestamp.

**Authentication:** Not required.

**Method:** `GET`

**Path:** `/health`

**Query Parameters:** None.

**Request Example:**

```
GET /health HTTP/1.1
Host: localhost:8000
```

```bash
curl http://localhost:8000/health
```

**Response Schema:**

| Field       | Type   | Description                          |
|-------------|--------|--------------------------------------|
| `status`    | string | Service health status                |
| `version`   | string | API version identifier               |
| `timestamp` | string | Current server time (ISO 8601 w/ tz) |

**Response Example (200 OK):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-15T14:23:01+00:00"
}
```

**Error Cases:** None. This endpoint always returns 200 if the service is running.

---

### GET /api/v1/workers

Returns a paginated list of employee and clinician records from the simulated HRIS.

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/workers`

**Query Parameters:**

| Parameter     | Type   | Required | Default | Description                                                                                          |
|---------------|--------|----------|---------|------------------------------------------------------------------------------------------------------|
| `page`        | int    | No       | 1       | Page number (1-indexed).                                                                             |
| `page_size`   | int    | No       | 100     | Number of records per page (max 500).                                                                |
| `location_id` | string | No       | --      | Filter by location (e.g., `"LOC-014"`).                                                             |
| `role_type`   | string | No       | --      | Filter by role. Enum: `Provider`, `RN`, `MA`, `RadTech`, `OfficeMgr`, `FrontDesk`.                  |
| `status`      | string | No       | --      | Filter by employment status. Enum: `Active`, `Terminated`, `Leave`.                                  |

**Request Example:**

```
GET /api/v1/workers?page=1&page_size=50&role_type=Provider&status=Active HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/workers?page=1&page_size=50&role_type=Provider&status=Active"
```

**Response Schema (data array element):**

| Field                 | Type        | Description                                          |
|-----------------------|-------------|------------------------------------------------------|
| `employee_id`         | string      | Unique employee identifier (e.g., `"EMP-00142"`).   |
| `first_name`          | string      | Employee first name.                                 |
| `last_name`           | string      | Employee last name.                                  |
| `email`               | string      | Employee email address.                              |
| `hire_date`           | string      | Date of hire (ISO 8601 date).                        |
| `termination_date`    | string/null | Date of termination, or `null` if still employed.    |
| `status`              | string      | Employment status: `Active`, `Terminated`, `Leave`.  |
| `role_type`           | string      | Role category (see enum above).                      |
| `job_title`           | string      | Specific job title (e.g., `"Nurse Practitioner"`).   |
| `job_level`           | string      | Job level or band.                                   |
| `schedule_type`       | string      | Schedule classification (e.g., `"Full-Time"`).       |
| `location_id`         | string      | Assigned location identifier.                        |
| `manager_employee_id` | string/null | Employee ID of direct manager, or `null`.            |
| `is_people_manager`   | boolean     | Whether this employee manages other employees.       |

**Response Example (200 OK):**

```json
{
  "data": [
    {
      "employee_id": "EMP-00142",
      "first_name": "Sarah",
      "last_name": "Chen",
      "email": "sarah.chen@wellnow.example.com",
      "hire_date": "2022-03-14",
      "termination_date": null,
      "status": "Active",
      "role_type": "Provider",
      "job_title": "Nurse Practitioner",
      "job_level": "Senior",
      "schedule_type": "Full-Time",
      "location_id": "LOC-014",
      "manager_employee_id": "EMP-00008",
      "is_people_manager": false
    },
    {
      "employee_id": "EMP-00307",
      "first_name": "James",
      "last_name": "Rivera",
      "email": "james.rivera@wellnow.example.com",
      "hire_date": "2021-08-02",
      "termination_date": null,
      "status": "Active",
      "role_type": "Provider",
      "job_title": "Physician Assistant",
      "job_level": "Mid",
      "schedule_type": "Full-Time",
      "location_id": "LOC-027",
      "manager_employee_id": "EMP-00008",
      "is_people_manager": false
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_records": 186,
    "total_pages": 4
  }
}
```

**Error Cases:**

| Status | Condition                              | Example `details`                                              |
|--------|----------------------------------------|----------------------------------------------------------------|
| 400    | Invalid `role_type` enum value         | `"Invalid role_type 'Doctor'. Must be one of: Provider, RN, MA, RadTech, OfficeMgr, FrontDesk."` |
| 400    | Invalid `status` enum value            | `"Invalid status 'Fired'. Must be one of: Active, Terminated, Leave."` |
| 401    | Missing or invalid API key             | `"Missing or invalid API key. Provide a valid X-API-Key header."` |
| 422    | `page_size` exceeds maximum            | FastAPI validation error.                                      |

---

### GET /api/v1/workers/{employee_id}

Returns a single employee record by employee ID.

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/workers/{employee_id}`

**Path Parameters:**

| Parameter     | Type   | Required | Description                                          |
|---------------|--------|----------|------------------------------------------------------|
| `employee_id` | string | Yes      | The unique employee identifier (e.g., `"EMP-00142"`). |

**Request Example:**

```
GET /api/v1/workers/EMP-00142 HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/workers/EMP-00142"
```

**Response Schema:**

Same fields as the worker object described in [GET /api/v1/workers](#get-apiv1workers). Returned as a single object (not wrapped in a `data` array or pagination envelope).

**Response Example (200 OK):**

```json
{
  "employee_id": "EMP-00142",
  "first_name": "Sarah",
  "last_name": "Chen",
  "email": "sarah.chen@wellnow.example.com",
  "hire_date": "2022-03-14",
  "termination_date": null,
  "status": "Active",
  "role_type": "Provider",
  "job_title": "Nurse Practitioner",
  "job_level": "Senior",
  "schedule_type": "Full-Time",
  "location_id": "LOC-014",
  "manager_employee_id": "EMP-00008",
  "is_people_manager": false
}
```

**Error Cases:**

| Status | Condition                  | Example `details`                                              |
|--------|----------------------------|----------------------------------------------------------------|
| 401    | Missing or invalid API key | `"Missing or invalid API key. Provide a valid X-API-Key header."` |
| 404    | Employee ID not found      | `"Employee 'EMP-99999' not found."`                            |

**Error Response Example (404):**

```json
{
  "error": {
    "code": 404,
    "message": "Not Found",
    "details": "Employee 'EMP-99999' not found."
  }
}
```

---

### GET /api/v1/schedules

Returns paginated scheduled and actual shift data for employees.

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/schedules`

**Query Parameters:**

| Parameter     | Type   | Required | Default | Description                                             |
|---------------|--------|----------|---------|---------------------------------------------------------|
| `start_date`  | string | Yes      | --      | Start of date range, inclusive (ISO 8601: `YYYY-MM-DD`).|
| `end_date`    | string | Yes      | --      | End of date range, inclusive (ISO 8601: `YYYY-MM-DD`).  |
| `location_id` | string | No       | --      | Filter by location (e.g., `"LOC-014"`).                 |
| `page`        | int    | No       | 1       | Page number (1-indexed).                                |
| `page_size`   | int    | No       | 100     | Number of records per page (max 500).                   |

**Request Example:**

```
GET /api/v1/schedules?start_date=2024-06-01&end_date=2024-06-07&location_id=LOC-014&page=1&page_size=50 HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/schedules?start_date=2024-06-01&end_date=2024-06-07&location_id=LOC-014"
```

**Response Schema (data array element):**

| Field             | Type        | Description                                                    |
|-------------------|-------------|----------------------------------------------------------------|
| `schedule_id`     | string      | Unique schedule entry identifier.                              |
| `employee_id`     | string      | Employee assigned to this shift.                               |
| `location_id`     | string      | Location of the shift.                                         |
| `shift_date`      | string      | Date of the shift (ISO 8601 date).                             |
| `shift_window`    | string      | Time-of-day window: `AM`, `PM`, or `Evening`.                  |
| `scheduled_start` | string      | Planned shift start time (ISO 8601 timestamp w/ tz).           |
| `scheduled_end`   | string      | Planned shift end time (ISO 8601 timestamp w/ tz).             |
| `actual_start`    | string/null | Actual clock-in time, or `null` if not worked.                 |
| `actual_end`      | string/null | Actual clock-out time, or `null` if not worked.                |
| `scheduled_hours` | float       | Planned hours for the shift.                                   |
| `actual_hours`    | float/null  | Actual hours worked, or `null` if not worked.                  |
| `is_overtime`     | boolean     | Whether the shift included overtime.                           |
| `is_callout`      | boolean     | Whether the employee called out (did not work the shift).      |
| `overtime_hours`  | float       | Number of overtime hours in this shift (0.0 if none).          |

**Response Example (200 OK):**

```json
{
  "data": [
    {
      "schedule_id": "SCH-20240601-00142-AM",
      "employee_id": "EMP-00142",
      "location_id": "LOC-014",
      "shift_date": "2024-06-01",
      "shift_window": "AM",
      "scheduled_start": "2024-06-01T08:00:00+00:00",
      "scheduled_end": "2024-06-01T16:00:00+00:00",
      "actual_start": "2024-06-01T07:55:00+00:00",
      "actual_end": "2024-06-01T16:32:00+00:00",
      "scheduled_hours": 8.0,
      "actual_hours": 8.62,
      "is_overtime": true,
      "is_callout": false,
      "overtime_hours": 0.62
    },
    {
      "schedule_id": "SCH-20240601-00307-PM",
      "employee_id": "EMP-00307",
      "location_id": "LOC-014",
      "shift_date": "2024-06-01",
      "shift_window": "PM",
      "scheduled_start": "2024-06-01T12:00:00+00:00",
      "scheduled_end": "2024-06-01T20:00:00+00:00",
      "actual_start": null,
      "actual_end": null,
      "scheduled_hours": 8.0,
      "actual_hours": null,
      "is_overtime": false,
      "is_callout": true,
      "overtime_hours": 0.0
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_records": 112,
    "total_pages": 3
  }
}
```

**Error Cases:**

| Status | Condition                          | Example `details`                                              |
|--------|------------------------------------|----------------------------------------------------------------|
| 400    | Missing `start_date` or `end_date` | `"Both start_date and end_date are required."`                |
| 400    | Invalid date format                | `"Invalid date format for start_date. Use YYYY-MM-DD."`       |
| 400    | `start_date` after `end_date`      | `"start_date must be before or equal to end_date."`           |
| 401    | Missing or invalid API key         | `"Missing or invalid API key. Provide a valid X-API-Key header."` |
| 422    | Validation error                   | FastAPI validation error.                                      |

---

### GET /api/v1/patient-volume

Returns paginated daily patient visit counts and operational metrics.

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/patient-volume`

**Query Parameters:**

| Parameter     | Type   | Required | Default | Description                                             |
|---------------|--------|----------|---------|---------------------------------------------------------|
| `start_date`  | string | Yes      | --      | Start of date range, inclusive (ISO 8601: `YYYY-MM-DD`).|
| `end_date`    | string | Yes      | --      | End of date range, inclusive (ISO 8601: `YYYY-MM-DD`).  |
| `location_id` | string | No       | --      | Filter by location (e.g., `"LOC-014"`).                 |
| `page`        | int    | No       | 1       | Page number (1-indexed).                                |
| `page_size`   | int    | No       | 100     | Number of records per page (max 500).                   |

**Request Example:**

```
GET /api/v1/patient-volume?start_date=2024-06-01&end_date=2024-06-07&location_id=LOC-014 HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/patient-volume?start_date=2024-06-01&end_date=2024-06-07&location_id=LOC-014"
```

**Response Schema (data array element):**

| Field                   | Type   | Description                                      |
|-------------------------|--------|--------------------------------------------------|
| `location_id`           | string | Location identifier.                             |
| `date`                  | string | Date of the record (ISO 8601 date).              |
| `patient_visits`        | int    | Total patient visits for the day at this location.|
| `avg_wait_time_minutes` | float  | Average patient wait time in minutes.            |
| `walk_ins`              | int    | Number of walk-in visits.                        |
| `appointments`          | int    | Number of scheduled appointment visits.          |

**Response Example (200 OK):**

```json
{
  "data": [
    {
      "location_id": "LOC-014",
      "date": "2024-06-01",
      "patient_visits": 47,
      "avg_wait_time_minutes": 23.4,
      "walk_ins": 31,
      "appointments": 16
    },
    {
      "location_id": "LOC-014",
      "date": "2024-06-02",
      "patient_visits": 52,
      "avg_wait_time_minutes": 28.1,
      "walk_ins": 35,
      "appointments": 17
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_records": 7,
    "total_pages": 1
  }
}
```

**Error Cases:**

| Status | Condition                          | Example `details`                                              |
|--------|------------------------------------|----------------------------------------------------------------|
| 400    | Missing `start_date` or `end_date` | `"Both start_date and end_date are required."`                |
| 400    | Invalid date format                | `"Invalid date format for end_date. Use YYYY-MM-DD."`         |
| 401    | Missing or invalid API key         | `"Missing or invalid API key. Provide a valid X-API-Key header."` |
| 422    | Validation error                   | FastAPI validation error.                                      |

---

### GET /api/v1/locations

Returns the full list of location master data. This endpoint is not paginated because the dataset is small (approximately 80 locations).

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/locations`

**Query Parameters:** None.

**Request Example:**

```
GET /api/v1/locations HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/locations"
```

**Response Schema (array element):**

| Field                   | Type        | Description                                             |
|-------------------------|-------------|---------------------------------------------------------|
| `location_id`           | string      | Unique location identifier (e.g., `"LOC-014"`).        |
| `location_name`         | string      | Human-readable location name.                           |
| `region`                | string      | Geographic region grouping.                             |
| `state`                 | string      | U.S. state (two-letter abbreviation).                   |
| `metro_area`            | string      | Metropolitan area name.                                 |
| `location_type`         | string      | Type of facility (e.g., `"Urgent Care"`).               |
| `operating_hours_start` | string      | Daily opening time (e.g., `"08:00"`).                   |
| `operating_hours_end`   | string      | Daily closing time (e.g., `"20:00"`).                   |
| `days_open_per_week`    | int         | Number of days open per week.                           |
| `budgeted_provider_fte` | float       | Budgeted full-time equivalent count for providers.      |
| `budgeted_support_fte`  | float       | Budgeted full-time equivalent count for support staff.  |
| `opened_date`           | string      | Date the location opened (ISO 8601 date).               |
| `is_active`             | boolean     | Whether the location is currently active.               |

**Response Example (200 OK):**

```json
[
  {
    "location_id": "LOC-001",
    "location_name": "WellNow Syracuse East",
    "region": "Northeast",
    "state": "NY",
    "metro_area": "Syracuse",
    "location_type": "Urgent Care",
    "operating_hours_start": "08:00",
    "operating_hours_end": "20:00",
    "days_open_per_week": 7,
    "budgeted_provider_fte": 4.0,
    "budgeted_support_fte": 8.5,
    "opened_date": "2019-04-15",
    "is_active": true
  },
  {
    "location_id": "LOC-002",
    "location_name": "WellNow Rochester Central",
    "region": "Northeast",
    "state": "NY",
    "metro_area": "Rochester",
    "location_type": "Urgent Care",
    "operating_hours_start": "08:00",
    "operating_hours_end": "20:00",
    "days_open_per_week": 7,
    "budgeted_provider_fte": 3.5,
    "budgeted_support_fte": 7.0,
    "opened_date": "2018-11-01",
    "is_active": true
  }
]
```

**Error Cases:**

| Status | Condition                  | Example `details`                                              |
|--------|----------------------------|----------------------------------------------------------------|
| 401    | Missing or invalid API key | `"Missing or invalid API key. Provide a valid X-API-Key header."` |

---

### GET /api/v1/terminations

Returns paginated termination records within a date range.

**Authentication:** Required (`X-API-Key` header).

**Method:** `GET`

**Path:** `/api/v1/terminations`

**Query Parameters:**

| Parameter    | Type   | Required | Default | Description                                             |
|--------------|--------|----------|---------|---------------------------------------------------------|
| `start_date` | string | Yes      | --      | Start of date range, inclusive (ISO 8601: `YYYY-MM-DD`).|
| `end_date`   | string | Yes      | --      | End of date range, inclusive (ISO 8601: `YYYY-MM-DD`).  |
| `page`       | int    | No       | 1       | Page number (1-indexed).                                |
| `page_size`  | int    | No       | 100     | Number of records per page (max 500).                   |

**Request Example:**

```
GET /api/v1/terminations?start_date=2024-01-01&end_date=2024-06-30&page=1&page_size=50 HTTP/1.1
Host: localhost:8000
X-API-Key: your-api-key-here
```

```bash
curl -H "X-API-Key: your-api-key-here" \
  "http://localhost:8000/api/v1/terminations?start_date=2024-01-01&end_date=2024-06-30"
```

**Response Schema (data array element):**

| Field              | Type   | Description                                                       |
|--------------------|--------|-------------------------------------------------------------------|
| `employee_id`      | string | Employee identifier of the terminated employee.                   |
| `termination_date` | string | Date of termination (ISO 8601 date).                              |
| `reason`           | string | High-level termination reason: `Voluntary`, `Involuntary`, `Retirement`. |
| `exit_type`        | string | Specific exit classification: `Resignation`, `Dismissal`, `RIF`, `Retirement`. |

**Response Example (200 OK):**

```json
{
  "data": [
    {
      "employee_id": "EMP-00089",
      "termination_date": "2024-02-14",
      "reason": "Voluntary",
      "exit_type": "Resignation"
    },
    {
      "employee_id": "EMP-00451",
      "termination_date": "2024-03-30",
      "reason": "Involuntary",
      "exit_type": "Dismissal"
    },
    {
      "employee_id": "EMP-00672",
      "termination_date": "2024-05-15",
      "reason": "Retirement",
      "exit_type": "Retirement"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_records": 78,
    "total_pages": 2
  }
}
```

**Error Cases:**

| Status | Condition                          | Example `details`                                              |
|--------|------------------------------------|----------------------------------------------------------------|
| 400    | Missing `start_date` or `end_date` | `"Both start_date and end_date are required."`                |
| 400    | Invalid date format                | `"Invalid date format for start_date. Use YYYY-MM-DD."`       |
| 401    | Missing or invalid API key         | `"Missing or invalid API key. Provide a valid X-API-Key header."` |
| 422    | Validation error                   | FastAPI validation error.                                      |

---

## Pagination Specification

The following rules apply to all paginated endpoints (`/workers`, `/schedules`, `/patient-volume`, `/terminations`):

| Property           | Value                                                           |
|--------------------|-----------------------------------------------------------------|
| Default page size  | 100 records per page.                                           |
| Maximum page size  | 500 records per page.                                           |
| Page indexing      | 1-indexed. The first page is `page=1`.                          |
| Out-of-range pages | Returns an empty `data` array with correct `total_records`.     |

**Pagination metadata** is always included in the response:

```json
{
  "pagination": {
    "page": 2,
    "page_size": 100,
    "total_records": 1200,
    "total_pages": 12
  }
}
```

- `total_records`: The total count of records matching the query (across all pages).
- `total_pages`: Calculated as `ceil(total_records / page_size)`.

---

## Error Response Format

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": <int>,
    "message": "<string>",
    "details": "<string or null>"
  }
}
```

### HTTP Status Codes

| Status Code | Meaning              | When Returned                                                       |
|-------------|----------------------|---------------------------------------------------------------------|
| 400         | Bad Request          | Invalid query parameters (bad date format, invalid enum, etc.).     |
| 401         | Unauthorized         | Missing or invalid `X-API-Key` header.                              |
| 404         | Not Found            | Requested resource does not exist (e.g., unknown `employee_id`).    |
| 422         | Validation Error     | FastAPI request validation failure (type mismatch, constraint violation). |
| 500         | Internal Server Error| Unexpected server-side error.                                       |

### Error Examples

**400 Bad Request:**

```json
{
  "error": {
    "code": 400,
    "message": "Bad Request",
    "details": "Invalid date format for start_date. Use YYYY-MM-DD."
  }
}
```

**401 Unauthorized:**

```json
{
  "error": {
    "code": 401,
    "message": "Unauthorized",
    "details": "Missing or invalid API key. Provide a valid X-API-Key header."
  }
}
```

**404 Not Found:**

```json
{
  "error": {
    "code": 404,
    "message": "Not Found",
    "details": "Employee 'EMP-99999' not found."
  }
}
```

**422 Validation Error (FastAPI default format):**

```json
{
  "detail": [
    {
      "loc": ["query", "page_size"],
      "msg": "ensure this value is less than or equal to 500",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**500 Internal Server Error:**

```json
{
  "error": {
    "code": 500,
    "message": "Internal Server Error",
    "details": null
  }
}
```

---

## Rate Limiting

Rate limiting is **not implemented** in this proof-of-concept API. All requests are served without throttling.

In a production deployment, the following would be recommended:

- Per-key rate limits (e.g., 100 requests per minute per API key).
- HTTP 429 (Too Many Requests) response with `Retry-After` header when limits are exceeded.
- Rate limit headers in every response (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).

---

## Data Generation Notes

All data served by the simulated HRIS API is synthetically generated using the Python Faker library. The generation is fully deterministic and reproducible.

| Property                 | Value                                                          |
|--------------------------|----------------------------------------------------------------|
| Random seed              | `MASTER_SEED=42`                                               |
| Total employees          | Approximately 1,200 across all locations.                      |
| Total locations          | Approximately 80 WellNow Urgent Care locations.                |
| Historical data coverage | 18 months of schedule, patient volume, and termination records. |
| Reproducibility          | Running the data generator with the same seed produces identical output. |

Because the data is seeded, test assertions and integration checks can rely on stable record counts and values across runs.
