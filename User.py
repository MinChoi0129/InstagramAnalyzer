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
    def getFollowUsers(user_name, data):
        f = open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'r')
        g = open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'r')
        
        a = {user.strip() for user in f.readlines()}
        b = {user.strip() for user in g.readlines()}
        c = set(UserReader.getUserList(data['followers']))
        d = set(UserReader.getUserList(data['followings']))

        f.close(); g.close()
        
        return a, b, c, d

class UserWriter:
    @staticmethod
    def recordUserConnections(user_name, old_followers, old_followings, current_followers, current_followings):
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followers.dat', mode = 'a'), current_followers, old_followers)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/old_followings.dat', mode = 'a'), current_followings, old_followings)
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/latest_followers.dat', mode = 'w'), current_followers, [], mode='DIRTY')
        UserWriter.writeUserData(open(PATH_USER_DB + user_name + '/latest_followings.dat', mode = 'w'), current_followings, [], mode='DIRTY')

    @staticmethod
    def writeUserData(file_obj, iterator, comparator, mode=None):
        if mode:
            for user in iterator:
                if user not in comparator:
                    file_obj.write(user + '님의 프로필 사진\r\n')
            file_obj.close()
        else:
            for user in iterator:
                if user not in comparator:
                    file_obj.write(user + '\r\n')
            file_obj.close()

    @staticmethod
    def writeNewDirectoryAndFiles(req_user_name, req_password):
        with open(PATH_USER_DB + 'user_accounts.csv', mode='a') as f: f.write(req_user_name + ',' + req_password + '\n')
        mkdir(PATH_USER_DB + req_user_name)
        Path(PATH_USER_DB + req_user_name + '/old_followings.dat').touch()
        Path(PATH_USER_DB + req_user_name + '/old_followers.dat').touch()
        Path(PATH_USER_DB + req_user_name + '/latest_followings.dat').touch()
        Path(PATH_USER_DB + req_user_name + '/latest_followers.dat').touch()

class UserAnalyzer:
    @staticmethod
    def analyzeUserConnections(old_followers, old_followings, current_followers, current_followings):
        old_bi_follows = old_followers & old_followings # 과거에 한번이라도 맞팔한 적이 있는 유저들
        current_bi_follows = current_followings & current_followers # 지금 맞팔중인 유저들
        nickname_change_bi_follow = current_bi_follows - old_bi_follows # 아이디 변경한 유저
        un_bi_followed_by_others = old_bi_follows - current_bi_follows # 테스터가 맞팔해제 당하게 한 유저들
        just_unfollowed_by_others = old_followers - current_followers - un_bi_followed_by_others # 상대방 혼자 팔로우 하다가 혼자 팔로우 해제한 유저
        current_uni_follows_by_you = current_followings - current_followers # 지금 테스터만 팔로우 중인 유저들

        return [
            current_followers, # 지금 팔로워들
            current_followings, # 지금 팔로잉들
            current_bi_follows, # 지금 맞팔중인 유저들
            un_bi_followed_by_others, # 테스터가 맞팔해제 당하게 한 유저들 or 아이디 변경한 유저
            just_unfollowed_by_others, # 상대방만 혼자 팔로우 하다가 그 사람 혼자 팔로우 해제한 유저
            nickname_change_bi_follow, # 테스터를 새로 팔로우 하거나 아이디 변경한 유저
            current_uni_follows_by_you, # 지금 테스터만 팔로우 중인 유저들
        ]
    
    @staticmethod
    def generateUserAnalyzedHTML(req_user_name, result):
        txt = ""
        
        with open('./templates/analyzed_result.html', mode='r', encoding='utf-8') as f:
            while True:
                line = f.readline().strip()
                txt += line
                if line.startswith('</html>'): break

                if line.startswith('<div class="center_frame">'):
                    # 0, 1, 2
                    txt += f"<h2>팔로워 : {len(result[0])}, 팔로잉 : {len(result[1])}</h2><h2>맞팔로잉 : {len(result[2])}</h2>"

                    for user_set in result[3:]:
                        if user_set:

                            # 3
                            if user_set == result[3]: 
                                txt += "<h3>맞팔로우 취소한 유저(※주의※ : 아이디를 바꾼 유저일 수 있음)</h3><div class='show_box'>"
                                for user in user_set:
                                    txt += f'<form method="post" action="/removeUserFromUnBiFollowList">'
                                    txt += f'   <p><a href="https://www.instagram.com/{user}/" target="_blank">{user}</a></p>'
                                    txt += f'   <input type="hidden" name="req_user_name" value="{req_user_name}" />'
                                    txt += f'   <input type="hidden" name="target_name" value="{user}" />'
                                    txt += f'   <input type="submit" value="삭제" />'
                                    txt += f'</form>'

                            # 4, 5, 6
                            elif user_set == result[4]:
                                txt += "<h3>상대방 혼자 팔로우 하다가 혼자 팔로우 해제한 유저</h3><div class='show_box'>"
                                for user in user_set:
                                    txt += f'<form method="post" action="/removeUserFromUnBiFollowList">'
                                    txt += f'   <p><a href="https://www.instagram.com/{user}/" target="_blank">{user}</a></p>'
                                    txt += f'   <input type="hidden" name="req_user_name" value="{req_user_name}" />'
                                    txt += f'   <input type="hidden" name="target_name" value="{user}" />'
                                    txt += f'   <input type="submit" value="삭제" />'
                                    txt += f'</form>'


                            elif user_set == result[5]: txt += "<h3>회원님을 새로 팔로우 하거나 아이디를 바꾼 유저 목록(※주의※ : 이 항목은 이번만 나타남)</h3><div class='show_box'>"
                            elif user_set == result[6]: txt += f"<h3>회원님만 팔로우 중인 유저({len(user_set)}명)</h3><div class='show_box'>"
                            if user_set in result[5:]:
                                for user in user_set: txt += f'<p><a target="_blank" href="https://www.instagram.com/{user}/">{user}</a></p>'    

                            # close for class: show_box
                            txt += "</div>" 



                            '''
                            수정필요사항
                            result[5]: 첫 회원가입시에 나오면 안됨
                            removeUserFromUnBiFollowList 이름 바꾸기 bi가 아닐 수 있음
                            코드 긴 것 리팩토링
                            불필요 리팩토링 제거
                            삭제버튼 css 재설정
                            디렉토리 재 구조화
                            '''
            return txt