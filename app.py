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
        return redirect(url_for('success', action='signup'))
    return redirect(url_for('fail', action='signup'))

@app.route('/analyze', methods=['POST'])
def analyze():
    req_user_name = request.form['user_name'].strip()
    try:
        if UserReader.getUserAccountsDB()[req_user_name] == request.form['password'].strip():
            data = request.form
            full_of_follow_users = UserReader.getFollowUsers(req_user_name, data)
            UserWriter.recordUserConnections(req_user_name, *full_of_follow_users)
            return UserAnalyzer.generateUserAnalyzedHTML(req_user_name, UserAnalyzer.analyzeUserConnections(*full_of_follow_users))
        return redirect(url_for('fail', action='login')) 
    except:
        return redirect(url_for('fail', action='login')) 

@app.route('/fail/<action>', methods=['GET'])
def fail(action):
    return render_template(f'retry_{action}.html')

@app.route('/success/<action>', methods=['GET'])
def success(action):
    return render_template(f'success_{action}.html')

@app.route('/how_to_use')
def how_to_use():
    return render_template('how_to_use.html')

@app.route('/removeUserFromUnBiFollowList', methods=['POST'])
def removeUserFromUnBiFollowList():
    req_user_name, target_name = request.form['req_user_name'], request.form['target_name']

    F_PATH = PATH_USER_DB + req_user_name + '/old_followers.dat'
    G_PATH = PATH_USER_DB + req_user_name + '/old_followings.dat'

    with open(F_PATH, 'r', encoding='utf-8') as f, open(G_PATH, 'r', encoding='utf-8') as g:
        new_f = ''.join([user for user in f.readlines() if user.strip() != target_name])
        new_g = ''.join([user for user in g.readlines() if user.strip() != target_name])
    with open(F_PATH, 'w', encoding='utf-8') as f, open(G_PATH, 'w', encoding='utf-8') as g:
        f.write(new_f); g.write(new_g);


    with open(PATH_USER_DB + req_user_name + '/latest_followers.dat', 'r', encoding='utf-8') as f, \
         open(PATH_USER_DB + req_user_name + '/latest_followings.dat', 'r', encoding='utf-8') as g:
        
        data = {'followers': '\r\n'.join(f.readlines()), 'followings': '\r\n'.join(g.readlines())}
        full_of_follow_users = UserReader.getFollowUsers(req_user_name, data)
        return UserAnalyzer.generateUserAnalyzedHTML(req_user_name, UserAnalyzer.analyzeUserConnections(*full_of_follow_users))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)