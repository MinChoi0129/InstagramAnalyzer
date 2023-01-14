def getUserList(raw_data: str) -> list[str]:
    return [string[:string.find('님')] for string in raw_data.split('\r\n') if "프로필 사진" in string]

def getUserAccountsDB():
    with open('./static/user_db/user_accounts.csv', mode='r') as f:
        user_accounts = {}
        for line in f.readlines():
            user_name, password = line.split(',')
            if user_name in user_accounts:
                user_accounts[user_name].append(password)
            else:
                user_accounts[user_name] = [password]
        return user_accounts

def analyzeUserConnections(user_name, followers, followings):
    f = open('./static/user_db/' + user_name + '/old_followers.dat', mode = 'r')
    g = open('./static/user_db/' + user_name + '/old_followings.dat', mode = 'r')

    old_followers = set(f.readlines())
    old_followings = set(g.readlines())

    old_bifollows = old_followers & old_followings
    current_bifollows = followings & followers
    current_unifollows_by_you = followings - followers

    unbifollowed_by_others = old_bifollows - current_bifollows

    f.close(); g.close()

    f = open('./static/user_db/' + user_name + '/old_followers.dat', mode = 'a')
    g = open('./static/user_db/' + user_name + '/old_followings.dat', mode = 'a')

    for user in followers:
        if user not in old_followers:
            f.write(user + '\n')
    
    for user in followings:
        if user not in old_followings:
            g.write(user + '\n')
    
    
    
    f.close(); g.close()