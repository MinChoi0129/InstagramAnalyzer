from flask import Flask, render_template, request
from userFunctions import *
import os

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("create_account.html")
    elif request.method == 'POST':
        req_user_name, req_password = request.form['user_name'].strip(), request.form['password'].strip()

        if req_user_name in getUserAccountsDB():
            return render_template('retry_signup.html')
        else:
            with open('./static/user_db/user_accounts.csv', mode='a') as f: f.write(req_user_name + ',' + req_password + '\n')
            os.mkdir('./static/user_db/' + req_user_name)
            with open('./static/user_db/' + req_user_name + '/old_followings.dat', mode='w') as f: f.write('')
            with open('./static/user_db/' + req_user_name + '/old_followers.dat', mode='w') as f: f.write('')
            return render_template('success_signup.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    user_accounts = getUserAccountsDB()
    req_user_name, req_password = request.form['user_name'].strip(), request.form['password'].strip()

    if req_user_name in user_accounts and user_accounts[req_user_name] == req_password:
        current_followers = set(getUserList(request.form['followers']))
        current_followings = set(getUserList(request.form['followings']))
        main_point_result = analyzeAndRecordUserConnections(req_user_name, current_followers, current_followings)
        return generate_user_analyzed_html_text(main_point_result)
    else:
        return render_template('retry_login.html')

if __name__ == '__main__':
    app.run(debug=True, port=12345)