import pymysql
from admin import password

conn = pymysql.connect(host='127.0.0.1', user='root', password=password, db='INSTA_DB', charset='utf8', port=3306)
cur = conn.cursor()

try:
    cur.execute('CREATE TABLE user \
                (USERNAME CHAR(20) NOT NULL, \
                ENC_PASSWORD CHAR(120) NOT NULL, \
                OLD_FOLLOWERS MEDIUMTEXT, \
                OLD_FOLLOWINGS MEDIUMTEXT, \
                LATEST_FOLLOWERS MEDIUMTEXT, \
                LATEST_FOLLOWINGS MEDIUMTEXT) \
    ;')
    conn.commit()
except Exception as e:
    print(e)
    pass

HOST, PORT = '0.0.0.0', 12345


class UserReader:
    @staticmethod
    def getUserListFromRawData(raw_data): # CLEAR
        return [string[:string.find('님')].strip() for string in raw_data.split('\r\n') if "프로필 사진" in string]

    @staticmethod
    def getUserAccountsDB(): # CLEAR
        cur.execute("SELECT USERNAME, ENC_PASSWORD FROM user;")
        conn.commit()
        return {user_name: enc_password for user_name, enc_password in cur.fetchall()}

    @staticmethod
    def getFollowUsers(user_name, data=None): # CLEAR
        cur.execute(f'SELECT OLD_FOLLOWERS, OLD_FOLLOWINGS FROM user WHERE USERNAME="{user_name}";')
        conn.commit()
        fetched_data = cur.fetchall()[0]
        a, b = set(), set()
        if fetched_data[0] != None: a = set(fetched_data[0].split(','))
        if fetched_data[1] != None: b = set(fetched_data[1].split(','))

        if not data: return a, b
        cur.execute(f'SELECT LATEST_FOLLOWERS, LATEST_FOLLOWINGS FROM user WHERE USERNAME="{user_name}";')
        conn.commit()
        fetched_data = cur.fetchall()[0]
        a, b = fetched_data[0].split(','), fetched_data[1].split(',')
        c, d = UserReader.getUserListFromRawData(data['followers']), UserReader.getUserListFromRawData(data['followings'])
        return set(a), set(b), set(c), set(d)
    
class UserWriter:
    @staticmethod
    def recordUserConnections(user_name, mode, a=None, b=None, c=None, d=None):
        cmd = ""
        if mode == 'update_old_relationships': # a, b
            cmd = f'UPDATE user SET \
                    OLD_FOLLOWERS = "{a}", OLD_FOLLOWINGS = "{b}" \
                    WHERE USERNAME = "{user_name}";'
            
        elif mode == 'new_analyze': # a, b, c, d
            old_followers = ','.join(a)
            old_followings = ','.join(b)
            latest_followers = ','.join(c)
            latest_followings = ','.join(d)
            cmd = f'UPDATE user SET \
                    OLD_FOLLOWERS = "{old_followers}", OLD_FOLLOWINGS = "{old_followings}", \
                    LATEST_FOLLOWERS = "{latest_followers}", LATEST_FOLLOWINGS = "{latest_followings}" \
                    WHERE USERNAME = "{user_name}";'
            
        cur.execute(cmd)
        conn.commit()

    @staticmethod
    def addUserIntoDatabase(req_user_name, req_password): # CLEAR
        cur.execute(f'INSERT INTO user \
                    (USERNAME, ENC_PASSWORD, OLD_FOLLOWINGS, OLD_FOLLOWERS, LATEST_FOLLOWINGS, LATEST_FOLLOWERS) \
                    VALUES ("{req_user_name}", "{str(req_password)}", "", "", "", "")')
        conn.commit()
    
class UserAnalyzer:
    @staticmethod
    def analyzeUserConnections(m, n, p, q): # 조건 재분석 필요
        old_bi_follows = m & n #  과거 맞팔했던 유저
        current_bi_follows = p & q #  지금 맞팔중인 유저
        current_uni_follows_by_you = q - p #  지금 테스터만 팔로우 중인 유저

        new_followers = p - m
        nickname_changed = (p | q) - (m | n) #  아이디 변경한 유저
        new_followers -= nickname_changed # 테스터를 새로 팔로우 하는 유저(초기 분석은 포함하지 않도록 뒤에서 조건 처리 필요)

        disabled = (m | n) - (p | q) # 계정 비활성화한 유저
        uni_un_followed_by_others = (m - n) - (p - q) - disabled - nickname_changed #  상대방만 혼자 팔로우 하다가 그 사람 혼자 팔로우 해제한 유저(비활, 아이디 변경은 포함하지 않음)
        un_bi_followed_by_others = (m & n) - (p & q) - disabled - nickname_changed #  테스터가 맞팔해제 당하게 한 유저들(비활, 아이디 변경은 포함하지 않음)

        
        return_targets = [
            m, # ------------------------------------------  0 과거 팔로워
            n, # ------------------------------------------  1 과거 팔로잉
            p, # ------------------------------------------  2 지금 팔로워
            q, # ------------------------------------------  3 지금 팔로잉
            old_bi_follows, # -----------------------------  4 과거 맞팔했던 유저
            current_bi_follows, # -------------------------  5 지금 맞팔중인 유저

            new_followers, # ------------------------------  6 테스터를 새로 팔로우 하는 유저
            un_bi_followed_by_others, # -------------------  7 테스터가 맞팔해제 당하게 한 유저들(비활, 아이디 변경은 포함하지 않음)
            disabled, # -----------------------------------  8 계정 비활성화한 유저
            uni_un_followed_by_others, # ------------------  9 상대방만 혼자 팔로우 하다가 그 사람 혼자 팔로우 해제한 유저
            nickname_changed, # --------------------------- 10 아이디 변경한 유저 or 계정 다시 활성화한 유저
            current_uni_follows_by_you, # ----------------- 11 지금 테스터만 팔로우 중인 유저
        ]
        
        for target in return_targets:
            try: target.remove("")
            except: continue
        
        return return_targets

    @staticmethod
    def generateUserAnalyzedHTML(result): # 조건 재분석 필요
        txt = ""      
        with open('./templates/analyzed_result.html', mode='r', encoding='utf-8') as f:
            while True:
                line = f.readline().strip()
                txt += line
                if line.startswith('</html>'): break
                if line.startswith('<div class="center_frame">'):
                    txt += f"<h2>팔로워 : {len(result[2])}, 팔로잉 : {len(result[3])}</h2><h2>맞팔로잉 : {len(result[5])}</h2>"
                    
                    if result[6] and (result[0] or result[1]):
                        txt += f"<h3>회원님을 새로 팔로우하는 유저({len(result[6])})</h3><div class='show_box'>"
                        for user in result[6]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[7]:
                        txt += f"<h3>회원님과의 맞팔로우를 해제한 유저({len(result[7])})</h3><div class='show_box'>"
                        for user in result[7]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[8]:
                        txt += f"<h3>계정을 비활성화 또는 삭제한 유저({len(result[8])})</h3>"
                        txt += f"<h4>아이디를 변경한 유저일 수 있습니다.</h4><div class='show_box'>"
                        for user in result[8]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[9]:
                        txt += f"<h3>혼자 팔로우하다 혼자 해제한 유저({len(result[9])})</h3><div class='show_box'>"
                        for user in result[9]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[10] and (result[0] or result[1]):
                        txt += f"<h3>인스타그램 아이디를 변경한 유저({len(result[10])})</h3>"
                        txt += f"<h4>계정을 다시 활성화 한 유저일 수 있습니다.</h4><div class='show_box'>"
                        for user in result[10]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[11]:
                        txt += f"<h3>회원님만 팔로우중인 유저({len(result[11])})</h3><div class='show_box'>"
                        for user in result[11]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    
            return txt