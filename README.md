# Distributed Booking Service System

This repository contains the implementation of a distributed booking service system. The system includes event management, ticket booking, and payment processing functionalities. It is designed using Django and Django REST Framework (DRF) and follows a microservices approach for user authentication and validation.

---

## Architecture
![DSARCH](https://raw.githubusercontent.com/nati-d/booking_system_distributed_system/main/DSARCH.jpg)


# Microservices Documentation

| **Microservice** | **Responsibility**                                      | **API**                                                   | **Database Entities**                          | **Key Feature**                                            |
|-------------------|-----------------------------------------------------------|------------------------------------------------------------|---------------------------------------------------------|------------------------------------------------------------|
| **User Service**: 8000 | User registration and authentication, Profile management, Manage user roles | POST /users/register, POST /users/login, GET /users/{id}, PUT /users/{id} | id (PK), name, email (unique), passwordHash, role, createdAt, updatedAt | Handle user registration and authentication, Manage user data securely, Provide API access tokens for secure communication |
| **Booking Service**: 8001 | Create and manage bookings, Check availability, Handle cancellations and modifications | POST /bookings, GET /bookings/{id}, PUT /bookings/{id}, DELETE /bookings/{id}, GET /availability | id (PK), userId (FK), resourceId, startTime, endTime, status, createdAt, updatedAt | Manage booking lifecycle (create, update, cancel), Maintain resource availability, Communicate with the user and payment services for confirmation |
| **Notification Service** | Process notifications                                    | POST /notification                                         | id (PK), notification                                  | Handle and send notifications                                  |


## Features

### Event Management
- Create, update, retrieve, and delete events.
- List available events with tickets greater than zero, sorted by date.

### Booking System
- Book tickets for events.
- Maintain booking status: `pending`, `confirmed`, or `canceled`.
- Associate bookings with users via token-based authentication.

### Payment Processing
- Process payments for bookings with a `pending` status.
- Update booking status to `confirmed` after successful payment.
- Track payment details and statuses (`success`, `failed`, `pending`).

---

## Prerequisites

- Python 3.8+
- Django 4.0+
- Django REST Framework
- PostgreSQL (recommended for production)
- [Docker](https://www.docker.com/) (optional for containerized setup)

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/distributed-booking-service.git
   cd distributed-booking-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a PostgreSQL database (or SQLite for development).
   - Update `settings.py` with your database configuration.
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_database_name',
           'USER': 'your_database_user',
           'PASSWORD': 'your_database_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Endpoints

### Event Endpoints
- **List Events**: `/api/events/` (GET)
- **Event Details**: `/api/events/<id>/` (GET, PUT, DELETE)
- **Create Event**: `/api/events/create/` (POST)

### Booking Endpoints
- **Create Booking**: `/api/bookings/create/` (POST)
- **List User Bookings**: `/api/bookings/` (GET)

### Payment Endpoints
- **Process Payment**: `/api/payments/` (POST)

---

## JWT Authentication

The system uses JWT for secure authentication. Tokens are validated via an external user authentication service.

- Add the `Authorization` header to requests:
  ```
  Authorization: Bearer <your_jwt_token>
  ```

- Example of extracting the token in views:
  ```python
  token = self.request.headers.get("Authorization").split(" ")[1]
  ```

---

## Models Overview

### Event
- **Fields**:
  - `name`: Name of the event.
  - `description`: Description of the event.
  - `date`: Date of the event.
  - `time`: Time of the event.
  - `location`: Location of the event.
  - `total_tickets`: Total tickets available.
  - `available_tickets`: Tickets still available.
  - `price_per_ticket`: Cost per ticket.

### Booking
- **Fields**:
  - `user_id`: ID of the user who made the booking.
  - `event`: Event being booked.
  - `tickets_booked`: Number of tickets booked.
  - `status`: Status of the booking (`pending`, `confirmed`, `canceled`).

### Payment
- **Fields**:
  - `booking`: Related booking.
  - `amount`: Payment amount.
  - `status`: Payment status (`success`, `failed`, `pending`).

---

## Deployment

### Docker (Optional)

1. Build the Docker image:
   ```bash
   docker build -t booking-service .
   ```

2. Run the Docker container:
   ```bash
   docker run -p 8000:8000 booking-service
   ```

### Environment Variables

Set the following variables in your `.env` file:
```
SECRET_KEY=your_secret_key
DEBUG=True  # Set to False in production
DATABASE_URL=your_database_url
```

---

## Testing

Run unit tests to verify the functionality:
```bash
python manage.py test
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any suggestions or improvements.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any questions or inquiries, feel free to reach out:

- **Email**: your-email@example.com
- **GitHub**: [your-username](https://github.com/your-username)
