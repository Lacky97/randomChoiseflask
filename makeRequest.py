import requests

zeros = 0
ones = 0
x = True
while x:
    response = requests.get('http://192.168.0.109:5000/user/luca').text
    if response == '0':
        zeros += 1
    else:
        ones += 1
        x = False
    
print('crocie: ', ones)
print('testa: ', zeros)