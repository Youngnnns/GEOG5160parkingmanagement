
# Parking Management System

This project is a Django-based web application designed to manage parking spaces efficiently. It allows users to book parking spots, manage their reservations, and view parking availability.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration and authentication
- Parking spot booking and management
- Real-time parking availability
- Admin panel for managing users and parking spots
- Responsive design for mobile and desktop use

## Technologies Used

- **Python**: 3.x
- **Django**: 3.x
- **Bootstrap**: for frontend design
- **SQLite**: default database, can be replaced with PostgreSQL or MySQL
- **GitHub Actions**: for CI/CD

## Installation

To run this project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Youngnnns/GEOG5160parkingmanagement.git
   cd GEOG5160parkingmanagement
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   
   Open your browser and go to `http://127.0.0.1:8000/`.

## Usage

- After installation, visit the homepage to register a new user.
- Use the admin panel to manage parking spots and user reservations.
- Users can log in to book and view their parking reservations.

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request. All contributions are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/YourFeature`)
3. Commit your Changes (`git commit -m 'Add some YourFeature'`)
4. Push to the Branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
