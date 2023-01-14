from flask import Flask, render_template, request
from userFunctions import getUserList, getUserAccountsDB, analyzeUserConnections
import os
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    req_user_name, req_password = request.form['user_name'], request.form['password']

    user_accounts = getUserAccountsDB()
    # if req_user_name not in user_accounts or user_accounts[req_user_name][0].split() != req_password: return render_template("retry_login.html")
    # else:
    followers, followings = set(getUserList(request.form['follower'])), set(getUserList(request.form['following']))
    print(len(followers), len(followings))
    for user in (followings - followers):
        print(user)
    user_connections = analyzeUserConnections(req_user_name, followers, followings)
    return render_template("analyze.html", data = user_connections)
    
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("create_account.html")
    elif request.method == 'POST':
        req_user_name, req_password = request.form['user_name'], request.form['password']
        with open('./static/user_db/user_accounts.csv', mode='r') as f:
            user_accounts = {}
            for line in f.readlines():
                user_name, password = line.split(',')
                if user_name in user_accounts:
                    user_accounts[user_name].append(password)
                else:
                    user_accounts[user_name] = [password]
        
        if req_user_name in user_accounts:
            return render_template('retry_signup.html')
        else:
            with open('./static/user_db/user_accounts.csv', mode='a') as f: f.write(req_user_name + ',' + req_password + '\n')
            os.mkdir('./static/user_db/' + req_user_name)
            with open('./static/user_db/' + req_user_name + '/old_followings.dat', mode='w') as f: f.write('')
            with open('./static/user_db/' + req_user_name + '/old_followers.dat', mode='w') as f: f.write('')
            return render_template('success_signup.html') 

if __name__ == '__main__':
    app.run(debug=True, port=8000)