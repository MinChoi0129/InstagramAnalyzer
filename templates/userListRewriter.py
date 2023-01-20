import sys

def rewrite(user_name, target_name):
    f = open('../static/user_db/' + user_name + '/old_followers.dat', 'r+', encoding='utf-8')
    g = open('../static/user_db/' + user_name + '/old_followings.dat', 'r+', encoding='utf-8')
    
    new_f = [user for user in f.readlines() if user != target_name]
    new_g = [user for user in f.readlines() if user != target_name]

    f.write(new_f); g.write(new_g);
    f.close(); g.close();