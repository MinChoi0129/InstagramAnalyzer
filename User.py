from flask import request
from pathlib import Path
from os import mkdir

PATH_USER_DB = './static/user_db/'

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
    def getFollowUsers(user_name, time_mode=None, relative_mode=None, full=False):
        f = open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'r')
        g = open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'r')
        
        a = {user.strip() for user in f.readlines()}
        b = {user.strip() for user in g.readlines()}
        c = set(UserReader.getUserList(request.form['followers']))
        d = set(UserReader.getUserList(request.form['followings']))

        f.close(); g.close()
        
        if full: return a, b, c, d
        
        if time_mode == 'old':
            if relative_mode == 'follower': return a
            elif relative_mode == 'following': return b
            elif relative_mode == 'both': return a, b
        elif time_mode == 'current':
            if relative_mode == 'follower': return c
            elif relative_mode == 'following': return d
            elif relative_mode == 'both': return c, d

class UserWriter:
    @staticmethod
    def recordUserConnections(user_name, old_followers, old_followings, current_followers, current_followings):
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'a'), current_followers, old_followers)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'a'), current_followings, old_followings)

    @staticmethod
    def writeUserData(file_obj, iterator, comparator):
        for user in iterator:
            if user not in comparator:
                file_obj.write(user + '\n')
        file_obj.close()

    @staticmethod
    def writeNewDirectoryAndFiles(req_user_name, req_password):
        with open(PATH_USER_DB + 'user_accounts.csv', mode='a') as f: f.write(req_user_name + ',' + req_password + '\n')
        mkdir(PATH_USER_DB + req_user_name)
        Path(PATH_USER_DB + req_user_name + '/old_followings.dat').touch()
        Path(PATH_USER_DB + req_user_name + '/old_followers.dat').touch()

class UserAnalyzer:
    @staticmethod
    def analyzeUserConnections(old_followers, old_followings, current_followers, current_followings):
        old_bi_follows = old_followers & old_followings # 과거에 한번이라도 맞팔한 적이 있는 유저들
        current_bi_follows = current_followings & current_followers # 지금 맞팔중인 유저들
        un_bi_followed_by_others = old_bi_follows - current_bi_follows # 테스터가 맞팔해제 당하게 한 유저들
        current_uni_follows_by_you = current_followings - current_followers # 지금 테스터만 팔로우 중인 유저들

        return [
            current_followers, # 지금 팔로워들
            current_followings, # 지금 팔로잉들
            current_bi_follows, # 지금 맞팔중인 유저들
            un_bi_followed_by_others, # 테스터가 맞팔해제 당하게 한 유저들 or 아이디 변경한 유저
            current_uni_follows_by_you, # 지금 테스터만 팔로우 중인 유저들
        ]
    
    @staticmethod
    def generateUserAnalyzedHTML(result):
        txt = ""
        
        with open('./templates/analyzed_result.html', mode='r', encoding='utf-8') as f:
            while True:
                line = f.readline().strip()
                txt += line
                if line.startswith('</html>'): break
                if line.startswith('<div class="center_frame">'):
                    txt += f"<h2>팔로워 : {len(result[0])}, 팔로잉 : {len(result[1])}</h2>"
                    txt += f"<h2>맞팔로잉 : {len(result[2])}</h2>"
                    for user_set in [result[3], result[4]]:
                        if len(user_set) > 0 and user_set == result[3]: txt += "<h3>맞팔로우 취소한 유저 또는 아이디 변경으로인해 확인해야할 유저 목록</h3>"
                        elif len(user_set) > 0 and user_set == result[4]: txt += "<h3>고객님만 팔로우 중인 유저 목록</h3>"
                        
                        txt += "<div class='show_box' style='border: 4px dotted yellow; width: 400px;'>"
                        for user in user_set:
                            txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'
                        txt += "</div>"
            return txt