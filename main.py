from flask import Flask, render_template, request, redirect, url_for
from User import *

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET': return render_template('signup.html')
    
    req_user_name, req_password = request.form['user_name'].strip(), request.form['password'].strip()    
    if req_user_name not in UserReader.getUserAccountsDB():
        UserWriter.writeNewDirectoryAndFiles(req_user_name, req_password)
        return redirect(url_for('success', action='login'))
    return redirect(url_for('fail', action='signup'))

@app.route('/analyze/<user_name>', methods=['GET', 'POST'])
def analyze(user_name):
    if request.method == 'GET':
        full_of_follow_users = UserReader.getFollowUsers(user_name, full=True)
        UserWriter.recordUserConnections(user_name, *full_of_follow_users)
        return UserAnalyzer.generateUserAnalyzedHTML(UserAnalyzer.analyzeUserConnections(*full_of_follow_users))
    elif request.method == 'POST':
        req_user_name = request.form['user_name'].strip()
        try:
            if UserReader.getUserAccountsDB()[req_user_name] == request.form['password'].strip():
                return redirect(url_for('analyze', user_name=req_user_name))
            return redirect(url_for('fail', action='login')) 
        except:
            return redirect(url_for('fail', action='login')) 

@app.route('/fail/<action>', methods=['GET'])
def fail(action):
    return render_template(f'retry_{action}.html')

@app.route('/success/<action>', methods=['GET'])
def success(action):
    return render_template(f'success_{action}.html')

if __name__ == '__main__':
    app.run(debug=True, port=12345)