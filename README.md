# Doctor Appointment API

This project is a FastAPI-based API for managing doctor appointments. It includes features for user registration, authentication, role-based access control, doctor availability management, and appointment booking.

## Features

- **User Management**: Register as a Doctor or Patient.
- **Authentication**: Secure login with JWT (JSON Web Tokens).
- **Role-Based Access Control (RBAC)**: Distinct permissions for Doctors and Patients.
- **Availability Management**: Doctors can set their weekly availability.
- **Appointment Booking**: Patients can view doctor availability and book appointments.
- **Appointment Management**: Patients and Doctors can cancel their appointments.
- **Password Management**: Mock forgot/reset password flow.

---

## 🚀 Setup and Installation

The project is fully containerized using Docker and Docker Compose, making setup straightforward.

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Environment Configuration (Recommended)

For better security, it's recommended to manage secrets using an environment file rather than hardcoding them in `docker-compose.yml`.

Create a file named `.env` in the project root:

```sh
# .env
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=doctor_db
MYSQL_USER=doctor_user
MYSQL_PASSWORD=doctor_pass
```

Then, update your `docker-compose.yml` to use these variables:

```yaml
# docker-compose.yml
services:
  mysql:
    # ...
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    # ...
  api:
    # ...
    environment:
      PYTHONUNBUFFERED: "1"
      DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
    # ...
```

Finally, add `.env` to your `.gitignore` file to prevent committing secrets to version control.

### 2. Build and Run the Application

Open your terminal in the project root and run the following command:

```sh
docker-compose up --build -d
```

- `--build`: Forces a rebuild of the `api` image, which is necessary when you change code or dependencies.
- `-d`: Runs the containers in detached mode (in the background).

### 3. Accessing the Services

- **API**: The API will be running at `http://localhost:8000`.
- **Interactive Docs (Swagger UI)**: You can access the interactive API documentation at `http://localhost:8000/docs`.
- **Database**: The MySQL database is exposed on your local machine at `localhost:3307`. You can connect to it with a database client using the credentials from your `.env` file.

### 4. Stopping the Application

- To stop the services:
  ```sh
  docker-compose down
  ```
- To stop the services and **delete all database data**:
  ```sh
  docker-compose down -v
  ```

---

## 🔐 Authentication and Authorization

### Authentication Flow

1.  **Registration (`POST /api/v1/auth/register`)**: A user registers with an email, password, and a `role` (`doctor` or `patient`). The password is automatically hashed using `bcrypt` before being stored.

2.  **Login (`POST /api/v1/auth/login`)**: The user logs in with their email and password.

3.  **JWT Generation**: Upon successful login, the server generates a JWT (JSON Web Token) containing the user's email (`sub`) and `role` in its payload. This token has a configured expiration time.

4.  **Authenticated Requests**: For all protected endpoints, the client must include the JWT in the `Authorization` header as a Bearer token.
    ```
    Authorization: Bearer <your_jwt_token>
    ```

### Role-Based Access Control (RBAC) Design

The application uses a clean, dependency-based approach for RBAC, leveraging the `role` claim embedded in the JWT. This avoids unnecessary database lookups on every request.

The core security dependencies are located in `app/api/dependencies.py` (or `app/api/v1/auth.py`):

1.  **`get_current_user`**:
    - This is the base security dependency.
    - It validates the JWT from the `Authorization` header.
    - It decodes the token, extracts the user's email (`sub`), and fetches the user object from the database.
    - If the token is invalid, expired, or the user doesn't exist, it raises a `401 Unauthorized` error.

2.  **`get_current_doctor`**:
    - This dependency first calls `get_current_user` to get the authenticated user.
    - It then checks if `current_user.role == Role.DOCTOR`.
    - If the user is not a doctor, it raises a `403 Forbidden` error.
    - **Usage**: Endpoints that should only be accessible by doctors (e.g., setting availability) use `Depends(get_current_doctor)`.

3.  **`get_current_patient`**:
    - This dependency works similarly to `get_current_doctor` but checks for the `PATIENT` role.
    - **Usage**: Endpoints that should only be accessible by patients (e.g., booking an appointment) use `Depends(get_current_patient)`.

This design ensures that endpoint logic remains clean while security and authorization are handled robustly and declaratively in the endpoint signature.

**Example from `appointment_api.py`:**
```python
@router.post("/book-appointments", ...)
def book_appointment(
    ...,
    current_patient: UserModel = Depends(get_current_patient),
):
    # This code will only run if the user is an authenticated patient.
```