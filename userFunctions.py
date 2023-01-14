def getUserList(raw_data: str) -> list[str]:
    return [string[:string.find('님')].strip() for string in raw_data.split('\r\n') if "프로필 사진" in string]

def getUserAccountsDB():
    with open('./static/user_db/user_accounts.csv', mode='r') as f:
        user_accounts = {}
        for line in f.readlines():
            user_name, password = line.split(',')
            user_accounts[user_name.strip()] = password.strip()
        return user_accounts

def record_user_connections(user_name, current_followers, current_followings, old_followers, old_followings):
    f = open('./static/user_db/' + user_name + '/old_followers.dat', mode = 'a')
    g = open('./static/user_db/' + user_name + '/old_followings.dat', mode = 'a')

    for user in current_followers:
        if user not in old_followers:
            f.write(user + '\n')
    
    for user in current_followings:
        if user not in old_followings:
            g.write(user + '\n')

    f.close(); g.close()
    
def analyzeAndRecordUserConnections(user_name: str, current_followers: set, current_followings: set):
    f = open('./static/user_db/' + user_name + '/old_followers.dat', mode = 'r')
    g = open('./static/user_db/' + user_name + '/old_followings.dat', mode = 'r')
    old_followers, old_followings = set(), set()
    for user in f.readlines(): old_followers.add(user.strip())
    for user in g.readlines(): old_followings.add(user.strip())
    f.close(); g.close()
    
    record_user_connections(user_name, current_followers, current_followings, old_followers, old_followings)
    
    # bi-follow
    old_bi_follows = old_followers & old_followings # 과거에 한번이라도 맞팔한 적이 있는 유저들
    current_bi_follows = current_followings & current_followers # 지금 맞팔중인 유저들
    
    # un-bi-follow
    un_bi_followed_by_you = current_bi_follows - old_bi_follows # 테스터때문에 맞팔해제 당한 유저들
    un_bi_followed_by_others = old_bi_follows - current_bi_follows # 테스터가 맞팔해제 당하게 한 유저들
    
    
    # uni-follow
    old_uni_follows_by_you = old_followings - old_followers # 옛날부터 검사직전까지 단 한번도 테스터를 팔로우하지 않은 유저들
    old_uni_follows_by_others = old_followers - old_followings # 옛날부터 검사직전까지 단 한번도 테스터가 팔로우하지 않은 유저들
    current_uni_follows_by_you = current_followings - current_followers # 지금 테스터만 팔로우 중인 유저들
    current_uni_follows_by_others = current_followers - current_followings # 지금 테스터를 팔로우 하지만, 정작 테스터 자신은 팔로우 하지 않는 유저들
    
    # un-uni-follow
    un_uni_followed_by_you = old_uni_follows_by_you - current_uni_follows_by_you # 맞팔로 변했거나, 그냥 둘 사이의 관계가 모두 사라진 경우
    un_uni_followed_by_others = old_uni_follows_by_others - current_uni_follows_by_others # 그냥 둘 사이의 관계가 모두 사라졌거나, 맞팔로 변한 경우
    
    return [
        current_followers, # 지금 팔로워들
        current_followings, # 지금 팔로잉들
        current_bi_follows, # 지금 맞팔중인 유저들
        un_bi_followed_by_others, # 테스터가 맞팔해제 당하게 한 유저들
        old_uni_follows_by_you, # 옛날부터 검사직전까지 단 한번도 테스터를 팔로우하지 않은 유저들
        current_uni_follows_by_you, # 지금 테스터만 팔로우 중인 유저들
        un_uni_followed_by_you # 맞팔로 변했거나, 그냥 둘 사이의 관계가 모두 사라진 경우(확인 필요)
    ]
    
def generate_user_analyzed_html_text(result: list):
    current_followers, current_followings, \
    current_bi_follows, un_bi_followed_by_others,\
    old_uni_follows_by_you, current_uni_follows_by_you, un_uni_followed_by_you = result
    """
    current_followers, # 지금 팔로워들
    current_followings, # 지금 팔로잉들
    current_bi_follows, # 지금 맞팔중인 유저들
    un_bi_followed_by_others, # 테스터가 맞팔해제 당하게 한 유저들
    old_uni_follows_by_you, # 옛날부터 검사직전까지 단 한번도 테스터를 팔로우하지 않은 유저들
    current_uni_follows_by_you, # 지금 테스터만 팔로우 중인 유저들
    un_uni_followed_by_you # 맞팔로 변했거나, 그냥 둘 사이의 관계가 모두 사라진 경우(확인 필요)
    """
    
    txt = ""
    
    f = open('./templates/analyzed_result.html', mode='r', encoding='utf-8')
    
    while True:
        line = f.readline().strip()
        
        if line.startswith('<div class="center_frame">'):
            txt += line
            break
        
        txt += line
    
    txt += f"<h2>팔로워 : {len(current_followers)}, 팔로잉 : {len(current_followings)}</h2>"
    
    # txt += "<h3>지금 맞팔중인 유저들</h3>"
    # for user in current_bi_follows:
    #     txt += f'<p>{user}</p>'

    txt += "<h3>테스터가 맞팔해제 당하게 한 유저들</h3>"
    for user in un_bi_followed_by_others:
        txt += f'<p>{user}</p>'
        
    txt += "<h3>가입일 이후부터 검사직전까지 단 한번도 테스터를 팔로우하지 않은 유저들</h3>"
    for user in old_uni_follows_by_you:
        txt += f'<p>{user}</p>'
        
    txt += "<h3>지금 테스터만 팔로우 중인 유저들</h3>"
    for user in current_uni_follows_by_you:
        txt += f'<p>{user}</p>'
        
    txt += "<h3>맞팔로 변했거나, 그냥 둘 사이의 관계가 모두 사라진 경우(확인 필요)</h3>"
    for user in un_uni_followed_by_you:
        txt += f'<p>{user}</p>'

    txt += '</div></body></html>'
    f.close()
    txt.strip('.')
    txt.replace("%7B%7B", "{" + "{")
    txt.replace("%7D%7D", "}" + "}")
    return txt