First make venv file in the project

script1:- python3 -m venv venv

script2:- source venv/bin/activate

script3:- pip3 install flask mysql-connector-python

script4:- pip3 install -r requirements.txt

script5:- pip3 install flask_mysqldb

app can be run through app.py
if __name__ == '__main__':
    app.run(debug=False) debug need to be true

admin can be register by link 
base_url/admin_signup
example http://127.0.0.1:5000/admin_signup

