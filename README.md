# KenLiz CareConnect

KenLiz CareConnect is a platform that connects healthcare professionals with health facilities and homes. 

## Features
- Register as a healthcare professional
- Register as a facility
- Admin CRUD operations
- Monthly updates for health workers' availability

## Getting Started

### Prerequisites
- Python 3.x
- Flask

### Installation
1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```sh
    cd KenLiz_CareConnect
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4. Set up the database:
    ```sh
    python
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```
5. Run the application:
    ```sh
    python app.py
    ```

### Deployment to Heroku

1. Log in to Heroku:
    ```sh
    heroku login
    ```
2. Create a new Heroku app:
    ```sh
    heroku create your-app-name
    ```
3. Add the Heroku Git remote:
    ```sh
    heroku git:remote -a your-app-name
    ```
4. Add a `Procfile` to the project root:
    ```
    web: python app.py
    ```
5. Push to Heroku:
    ```sh
    git add .
    git commit -m "Initial commit"
    git push heroku master
    ```
6. Open the app in your browser:
    ```sh
    heroku open
    ```

## License
This project is licensed under the MIT License.
