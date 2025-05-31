## Flask Session-Based Project (with Jinja2 & MySQL)
    This is a session-based web application built with Python Flask, Jinja2 templating, and MySQL for the backend database. The project uses a virtual environment for dependency isolation.

## Project Setup Instructions
##  1️⃣ Create a Virtual Environment
        python3 -m venv venv

##  2️⃣ Activate the Virtual Environment
        On Linux/macOS:
            source venv/bin/activate

        On Windows:
            venv\Scripts\activate

## Install Dependencies
    3️⃣ Manually Install Required Packages
        pip3 install flask mysql-connector-python

    4️⃣ (Optional) Install from requirements.txt
        pip3 install -r requirements.txt

        You can generate this file using:
        pip freeze > requirements.txt

## Configuration Note (MySQL Port)
    This project uses MySQL port 3307 in app.py:

    app.config['MYSQL_PORT'] = 3307 
        If your MySQL is running on port 3307, no changes needed otherwise delete it.

## Main Technologies Used
    Python 3, Flask, Jinja2, MySQL, flask_mysqldb, mysql-connector-python

## Set Up the Database
    Before running the application, you must create the database and required tables by importing the provided flask_mvc.sql file:
    just copy the sql query and run through mysqldb or
    mysql -u your_username -p your_database < flask_mvc.sql

⚠️ Important Note Before Running
    In your app.py, make sure to set debug mode to True while developing for detailed error messages and auto-reloading:

        if __name__ == '__main__':
            app.run(debug=True)

        Before deploying to production, change debug to False for security:

        if __name__ == '__main__':
            app.run(debug=False)

## Running the Application
    After activating your virtual environment and installing dependencies:
        python3 app.py

##  credentials for the user and admin login which is alread insert by the sample data
          email and password for admin

            Email: aswrya@gmail.com
            password: newone123

          email and password for user

            Email: samir@gmail.com
            password: samir@123

            Email2: jennifer@gmail.com
            password: jennifer@123

            Email3: akintunde@gmail.com
            password: akintunde@123

## Session-Based Authentication
    app.secret_key = 'your_secret_key'

## Admin Access & Features
Admin Signup
    You can register a new admin using this link:

        {{your_url}}/admin_signup

Admin Features
    Once logged in, the admin can:

    Add shops/vendors

    Add or delete food items

    View user messages

    Contact users via email

    Check and manage sales reports

## User Features
    Browse and order foods

    Search foods or drinks by item name

    Add items to a cart managed via Flask session

    Place orders through the web app

    Contact delivery personnel directly through the app

    View and manage cart contents before checkout
