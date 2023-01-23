from flask import Flask, render_template, request, redirect, url_for
from User import *
import bcrypt

app = Flask(__name__)

@app.route('/')
def main(): return render_template('index.html')

@app.route('/fail/<action>', methods=['GET'])
def fail(action): return render_template(f'retry_{action}.html')

@app.route('/success/<action>', methods=['GET'])
def success(action): return render_template(f'success_{action}.html')

@app.route('/how_to_use')
def how_to_use(): return render_template('how_to_use.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'GET': return render_template('signup.html')
    
    req_user_name, req_password = request.form['user_name'].strip(), request.form['password'].strip()
    encrypted_pw = bcrypt.hashpw(req_password.encode('UTF-8'), bcrypt.gensalt()).hex()
    if req_user_name not in UserReader.getUserAccountsDB():
        UserWriter.writeNewDirectoryAndFiles(req_user_name, encrypted_pw)
        return redirect(url_for('success', action='signup'))
    return redirect(url_for('fail', action='signup'))

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        req_user_name = request.form['user_name'].strip()
        if not bcrypt.checkpw(request.form['password'].strip().encode('UTF-8'), bytes.fromhex(UserReader.getUserAccountsDB()[req_user_name])): return redirect(url_for('fail', action='login'))
        data = request.form
        full_of_follow_users = UserReader.getFollowUsers(req_user_name, data)
        UserWriter.recordUserConnections(req_user_name, *full_of_follow_users)
        return UserAnalyzer.generateUserAnalyzedHTML(req_user_name, UserAnalyzer.analyzeUserConnections(*full_of_follow_users))
    except: return redirect(url_for('fail', action='login')) 

@app.route('/removeFromUnfollowList', methods=['POST'])
def removeFromUnfollowList():
    req_user_name, target_name = request.form['req_user_name'], request.form['target_name']

    OLD_F_PATH = PATH_USER_DB + req_user_name + '/old_followers.dat'
    OLD_G_PATH = PATH_USER_DB + req_user_name + '/old_followings.dat'
    NEW_F_PATH = PATH_USER_DB + req_user_name + '/latest_followers.dat'
    NEW_G_PATH = PATH_USER_DB + req_user_name + '/latest_followings.dat'

    with open(OLD_F_PATH, 'r', encoding='utf-8') as f, open(OLD_G_PATH, 'r', encoding='utf-8') as g: new_f, new_g = ''.join([user for user in f.readlines() if user.strip() != target_name]), ''.join([user for user in g.readlines() if user.strip() != target_name])
    with open(OLD_F_PATH, 'w', encoding='utf-8') as f, open(OLD_G_PATH, 'w', encoding='utf-8') as g: f.write(new_f); g.write(new_g);
    with open(NEW_F_PATH, 'r', encoding='utf-8') as f, open(NEW_G_PATH, 'r', encoding='utf-8') as g: return UserAnalyzer.generateUserAnalyzedHTML(req_user_name, UserAnalyzer.analyzeUserConnections(*UserReader.getFollowUsers(req_user_name, {'followers': '\r\n'.join(f.readlines()), 'followings': '\r\n'.join(g.readlines())})))
    
if __name__ == '__main__': app.run(host='0.0.0.0', port=12345)