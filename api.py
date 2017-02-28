import base64, hashlib, rsa, binascii
import requests
# import json
import tea

def getEncryption(password, salt_bytes, vcode):
    # salt_bytes是QQ号。
    puk = rsa.PublicKey(int(
        'F20CE00BAE5361F8FA3AE9CEFA495362'
        'FF7DA1BA628F64A347F0A8C012BF0B25'
        '4A30CD92ABFFE7A6EE0DC424CB6166F8'
        '819EFA5BCCB20EDFB4AD02E412CCF579'
        'B1CA711D55B8B0B3AEB60153D5E0693A'
        '2A86F3167D7847A0CB8B00004716A909'
        '5D9BADC977CBB804DBDCBA6029A97108'
        '69A453F27DFDDF83C016D928B3CBF4C7',
        16
    ), 3)
    e = int(salt_bytes).to_bytes(8, 'big')
    o = hashlib.md5(password.encode())
    r = bytes.fromhex(o.hexdigest())
    p = hashlib.md5(r + e).hexdigest()
    a = binascii.b2a_hex(rsa.encrypt(r, puk)).decode()
    s = hex(len(a) // 2)[2:]
    l = binascii.hexlify(vcode.upper().encode()).decode()
    c = hex(len(l) // 2)[2:]
    c = '0' * (4 - len(c)) + c
    s = '0' * (4 - len(s)) + s
    salt = s + a + binascii.hexlify(e).decode() + c + l
    return base64.b64encode(
        tea.encrypt(bytes.fromhex(salt), bytes.fromhex(p))
    ).decode().replace('/', '-').replace('+', '*').replace('=', '_')


headers = {
    'Host': 'ssl.ptlogin2.qq.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'connect': 'close'
}

vcodeHeaders = {
    'Host': 'ssl.captcha.qq.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'connect': 'close'
}

def getVer(username):
    # 检查用不用输入验证码。
    html = requests.get('https://ssl.ptlogin2.qq.com/check?regmaster=&pt_tea=1&pt_vcode=0&uin={0}&appid=522005705&js_ver=10151&js_type=1&login_sig=&u1=https%3A%2F%2Fmail.qq.com%2Fcgi-bin%2Flogin%3Fvt%3Dpassport%26vm%3Dwpt%26ft%3Dloginpage%26target%3D&r=0.31754892738536'.format(username))
    cookies = html.cookies

    # 
    ptui_checkVC = html.text.split(',')
    # 不需要验证码。
    if '0' in ptui_checkVC[0]:
        verifycode = ptui_checkVC[1][1:-1]
        # session = ptui_checkVC[3][1:-1]
        vcode = cookies.get('ptvfsession')
        return [0, verifycode, vcode, cookies]
        # return login_qq(username, password, verifycode, vcode, cookies)
    # 需要验证码。
    else:
        # 请求验证码并保存下来。
        vcode = ptui_checkVC[1][1:-1]
        verifycode_img = requests.get('https://ssl.captcha.qq.com/getimage?uin={0}&aid=522005705&cap_cd={1}&0.7659631329588592'.format(username, vcode), headers=vcodeHeaders, cookies=cookies)
        vcode = verifycode_img.cookies.get('verifysession')
        cookies.update(verifycode_img.cookies)
        with open('catch/verifycode.jpg', 'wb') as f:
            f.write(verifycode_img.content)

        return [1, vcode, cookies]
        # with open('aaa.jpg', 'wb') as f:
        #     f.write(verifycode_img.content)

        # verifycode = input("Input verifycode: ")

def login_qq(username, password, verifycode, vcode, cookies):


    # raw_salt = html.text.split(',')[2].split('\\x')
    # salt = raw_salt[1:-1] + [raw_salt[-1].strip("'")]
    # salt_bytes = ''.join(salt)

    password = getEncryption(password, username, verifycode)

    html = requests.get('https://ssl.ptlogin2.qq.com/login?u={0}&verifycode={1}&pt_vcode_v1=0&pt_verifysession_v1={2}&p={3}&pt_randsalt=0&u1=https%3A%2F%2Fmail.qq.com%2Fcgi-bin%2Flogin%3Fvt%3Dpassport%26vm%3Dwpt%26ft%3Dloginpage%26target%3D%26account%3D_qq&ptredirect=1&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=3-27-1457499465993&js_ver=10151&js_type=1&login_sig=&pt_uistyle=25&aid=522005705&daid=4&'.format(username, verifycode, vcode, password), headers=headers, cookies=cookies)
    respone = str(html.text)
    if '登录成功' in respone:
        return 'OK'
    elif '帐号或密码不正确' in respone:
        return 'NOPASS'
    else:
        return 'NOVER'

def run(username, password):

    verInfo = getVer(username)
    if verInfo[0] == 0:
        result = login_qq(username, password, verInfo[1], verInfo[2], verInfo[3])
    elif verInfo[0] == 1:
        verifycode = input("请输入验证码: ")
        result = login_qq(username, password, verifycode, verInfo[1], verInfo[2])

    return result

if __name__ == '__main__':
    username = input("请输入账号: ")
    password = input("请输入密码: ")
    print(run(username, password))