from flask import Flask, render_template, request, redirect, url_for
from User import UserReader as R, UserWriter as W, UserAnalyzer as A, HOST, PORT
from bcrypt import checkpw, hashpw, gensalt

app = Flask(__name__)

# Normal Functions
def removeFromOldRelationship(req_user_name, target_name):
    old_followers, old_followings = R.getFollowUsers(req_user_name)
    old_followers.remove(target_name)
    old_followings.remove(target_name)
    a, b = ','.join(old_followers), ','.join(old_followings)
    W.recordUserConnections(req_user_name, a = a, b = b, mode='update_old_relationships')

def signupResponse(req_user_name, req_password): # CLEAR
    if req_user_name in R.getUserAccountsDB(): return redirect(url_for('fail', action='signup'))
    W.addUserIntoDatabase(req_user_name, hashpw(req_password.encode('UTF-8'), gensalt()).hex())
    return redirect(url_for('success', action='signup'))



# Routers
@app.route('/')
def main(): # CLEAR
    return render_template('index.html')

@app.route('/fail/<action>', methods=['GET'])
def fail(action): # CLEAR
    return render_template(f'retry_{action}.html')

@app.route('/success/<action>', methods=['GET'])
def success(action): # CLEAR
    return render_template(f'success_{action}.html')

@app.route('/instruction')
def instruction(): # CLEAR, 사진 변경?
    return render_template('instruction.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup(): # CLEAR
    return render_template('signup.html') if request.method == 'GET' else signupResponse(request.form['user_name'], request.form['password'])
    
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        return removeFromOldRelationship(request.form['req_user_name'], request.form['target_name'])
    except:
        try:
            # 계정 검증
            req_user_name = request.form['user_name']
            req_password = request.form['password'].encode('UTF-8')
            db_password = bytes.fromhex(R.getUserAccountsDB()[req_user_name])
            if not checkpw(req_password, db_password): return redirect(url_for('fail', action='login'))

            # DB 및 form에서 정보 받기
            full_of_follow_users = R.getFollowUsers(req_user_name, request.form) # a, b, c, d
            W.recordUserConnections(req_user_name, 'new_analyze', *full_of_follow_users)
            return A.generateUserAnalyzedHTML(A.analyzeUserConnections(*full_of_follow_users))
        except KeyError: return redirect(url_for('fail', action='login')) 
        except Exception as e: return str(e)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)