from flask import Flask, render_template, request, redirect, url_for
from User import *

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST': 
        req_user_name, req_password = request.form['user_name'].strip(), request.form['password'].strip()    
        if req_user_name not in UserReader.getUserAccountsDB():
            UserWriter.writeNewDirectoryAndFiles(req_user_name, req_password)
            return render_template('success_signup.html')
        return render_template('retry_signup.html')
    return render_template('signup.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    req_user_name = request.form['user_name'].strip()
    try:
        if UserReader.getUserAccountsDB()[req_user_name] == request.form['password'].strip():
            full_of_follow_users = UserReader.getFollowUsers(req_user_name, full=True)
            UserWriter.recordUserConnections(req_user_name, *full_of_follow_users)
            result = UserAnalyzer.analyzeUserConnections(*full_of_follow_users)
            return UserAnalyzer.generateUserAnalyzedHTML(result)
        return redirect(url_for('loginfail')) 
    except:
        return redirect(url_for('loginfail')) 

@app.route('/loginfail', methods=['GET'])
def loginfail():
    return render_template('retry_login.html')

if __name__ == '__main__':
    app.run(debug=True, port=12345)