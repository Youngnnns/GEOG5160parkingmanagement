
# WebGIS-based map visualisation system for car park management in London
# 基于WebGIS的伦敦停车场管理地图可视化系统
注：该系统已部署在AWS平台，您可通过以下链接进入：http://18.175.159.102。
由于注册登录后才可进行预约按钮的显示，您可通过以下账号、密码进行登录（可以不用您自己执行注册）

Note: The system is deployed in AWS platform, you can access it via the following link: http://18.175.159.102.
Due to the registration and login before the booking button can be displayed, you can log in through the following account and password (you can not perform the registration yourself)

账号：ZhangSanD

Account number: ZhangSan

密码：@A123456y

Password: @A123456

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

- **Python**: 3.12
- **Django**: 5.1
- **Bootstrap**: for frontend design
- **SQLite**: PostgreSQL
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
