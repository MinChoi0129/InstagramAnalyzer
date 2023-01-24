from flask import Flask, render_template, request, redirect, url_for
from User import UserReader as R, UserWriter as W, UserAnalyzer as A, HOST, PORT
from bcrypt import checkpw, hashpw, gensalt

app = Flask(__name__)

# Normal Functions
def removeFromUnfollowList(req_user_name, target_name):
    OLD_F, OLD_G, NEW_F, NEW_G = R.getUserPaths(req_user_name)
    with open(OLD_F, 'r', encoding='utf-8') as f, open(OLD_G, 'r', encoding='utf-8') as g: data = [''.join([u for u in h.readlines() if u.strip() != target_name]) for h in [f, g]]
    with open(OLD_F, 'w', encoding='utf-8') as f, open(OLD_G, 'w', encoding='utf-8') as g: f.write(data[0]); g.write(data[1])
    with open(NEW_F, 'r', encoding='utf-8') as f, open(NEW_G, 'r', encoding='utf-8') as g:
        raw_data = {'followers': '\r\n'.join(f.readlines()), 'followings': '\r\n'.join(g.readlines())}
        analyze_result = A.analyzeUserConnections(*R.getFollowUsers(req_user_name, raw_data))
        return A.generateUserAnalyzedHTML(req_user_name, analyze_result)

def signupResponse(req_user_name, req_password):
    if req_user_name in R.getUserAccountsDB(): return redirect(url_for('fail', action='signup'))
    W.writeNewDirectoryAndFiles(req_user_name, hashpw(req_password.encode('UTF-8'), gensalt()).hex())
    return redirect(url_for('success', action='signup'))

# Routers
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/fail/<action>', methods=['GET'])
def fail(action):
    return render_template(f'retry_{action}.html')

@app.route('/success/<action>', methods=['GET'])
def success(action):
    return render_template(f'success_{action}.html')

@app.route('/instruction')
def instruction():
    return render_template('instruction.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    return render_template('signup.html') if request.method == 'GET' else signupResponse(request.form['user_name'].strip(), request.form['password'].strip())
    
@app.route('/analyze', methods=['POST'])
def analyze():
    try: return removeFromUnfollowList(request.form['req_user_name'], request.form['target_name'])
    except:
        try:
            req_user_name = request.form['user_name'].strip()
            req_password = request.form['password'].strip().encode('UTF-8')
            db_password = bytes.fromhex(R.getUserAccountsDB()[req_user_name])
            if not checkpw(req_password, db_password): return redirect(url_for('fail', action='login'))
            full_of_follow_users = R.getFollowUsers(req_user_name, request.form)
            W.recordUserConnections(req_user_name, *full_of_follow_users)
            return A.generateUserAnalyzedHTML(req_user_name, A.analyzeUserConnections(*full_of_follow_users))
        except KeyError: return redirect(url_for('fail', action='login')) 
        except Exception as e: return str(e)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)