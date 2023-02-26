from pathlib import Path
from os import mkdir
from difflib import SequenceMatcher

PATH_USER_DB = './static/user_db/'
HOST, PORT = '0.0.0.0', 12345

class UserReader:
    @staticmethod
    def getUserList(raw_data):
        return [string[:string.find('님')].strip() for string in raw_data.split('\r\n') if "프로필 사진" in string]

    @staticmethod
    def getUserAccountsDB():
        with open(PATH_USER_DB + 'user_accounts.csv', mode='r') as f:
            user_accounts = {}
            for line in f.readlines():
                user_name, password = line.split(',')
                user_accounts[user_name.strip()] = password.strip()
            return user_accounts

    @staticmethod
    def getFollowUsers(user_name, data):
        with open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'r') as f, open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'r') as g:
            a, b = {user.strip() for user in f.readlines()}, {user.strip() for user in g.readlines()}
            c, d = set(UserReader.getUserList(data['followers'])), set(UserReader.getUserList(data['followings']))
        return a, b, c, d
    
    @staticmethod
    def getUserPaths(req_user_name):
        return [PATH_USER_DB + req_user_name + detail for detail in ['/old_followers.dat', '/old_followings.dat', '/latest_followers.dat', '/latest_followings.dat']]

class UserWriter:
    @staticmethod
    def recordUserConnections(user_name, old_followers, old_followings, current_followers, current_followings):
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'a'), current_followers, old_followers)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'a'), current_followings, old_followings)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/latest_followers.dat', mode = 'w'), current_followers, [], long=True)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/latest_followings.dat', mode = 'w'), current_followings, [], long=True)

    @staticmethod
    def writeUserData(file_obj, iterator, comparator, long=None):
        tail = '님의 프로필 사진\r\n' if long else '\r\n'
        for user in iterator:
            if user not in comparator:
                file_obj.write(user + tail)
        file_obj.close()

    @staticmethod
    def writeNewDirectoryAndFiles(req_user_name, req_password):
        with open(PATH_USER_DB + 'user_accounts.csv', mode='a') as f: f.write(req_user_name + ',' + req_password + '\n')
        mkdir(PATH_USER_DB + req_user_name)
        for path in UserReader.getUserPaths(req_user_name):
            Path(path).touch()

class UserAnalyzer:
    @staticmethod
    def getSimilarity(user_list: set[str], target: str) -> tuple[str, float]: 
        stringHandle = lambda a: ''.join(''.join(a.strip().split('_')).split('.')).lower()
        answer_bytes = list(bytes(stringHandle(target), 'utf-8'))
        for input_string in map(stringHandle, user_list):
            input_bytes = list(bytes(input_string, 'utf-8'))
            similarity_percent = SequenceMatcher(None, answer_bytes, input_bytes).ratio() * 100
            if similarity_percent >= 55:
                return input_string, similarity_percent
        return None, None

    @staticmethod
    def analyzeUserConnections(m, n, p, q):
        old_bi_follows = m & n #  과거 맞팔했던 유저
        current_bi_follows = p & q #  지금 맞팔중인 유저
        current_uni_follows_by_you = q - p #  지금 테스터만 팔로우 중인 유저

        nickname_changed = (p | q) - (m | n) #  아이디 변경한 유저
        new_followers = p - m - nickname_changed # 테스터를 새로 팔로우 하는 유저(초기 분석은 포함하지 않도록 뒤에서 조건 처리 필요)
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
            nickname_changed, # --------------------------- 10 아이디 변경한 유저
            current_uni_follows_by_you, # ----------------- 11 지금 테스터만 팔로우 중인 유저
        ]
        
        for target in return_targets:
            try: target.remove("")
            except: continue
        
        return return_targets
            
    
    @staticmethod
    def generateUserAnalyzedHTML(result):
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
                        txt += f"<h3>인스타그램 아이디를 변경한 유저({len(result[10])})</h3><div class='show_box'>"
                        for user in result[10]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    if result[11]:
                        txt += f"<h3>회원님만 팔로우중인 유저({len(result[11])})</h3><div class='show_box'>"
                        for user in result[11]:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>" 
                    
            return txt





            # similar_user_name, similarity = UserAnalyzer.getSimilarity(result[4], user)
            # show_user_name =  + '(이전 아이디 : ' +  + ') - ' + str(similarity) + '%' if similar_user_name else user

            # for user in result[7]:
            #     txt += f'<form method="post" action="/analyze">'
            #     txt += f'   <p><a href="https://www.instagram.com/{user}/" target="_blank">{user}</a></p>'
            #     txt += f'   <input type="hidden" name="req_user_name" value="{req_user_name}" />'
            #     txt += f'   <input type="hidden" name="target_name" value="{user}" />'
            #     txt += f'   <input type="submit" value="삭제" />'
            #     txt += f'</form>'

            # for user in result[]:
            #     txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'