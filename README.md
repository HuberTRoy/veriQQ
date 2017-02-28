# 批量验证QQ密码

> 第三方依赖。
[rsa](https://pypi.python.org/pypi/rsa/), [requests](https://pypi.python.org/pypi/requests/)

> 可选:
[PYQT5](https://riverbankcomputing.com/software/pyqt/download5)

## 使用方法:

0.安装有PYQT5, 运行window.py。
导入文本:<br />
```
账号 密码
账号2 密码2
```
<img src='https://github.com/HuberTRoy/veriQQ/blob/master/showpic/0.jpg'>

无验证码会直接验证，有验证码需要手动输入验证码，验证码会在输入了4个字符后自动验证。<br />
<img src='https://github.com/HuberTRoy/veriQQ/blob/master/showpic/1.gif'>

1.没有安装PYQT5, 运行api.py.
直接运行可测试运行情况。验证码保存在当前目录的catch目录下。
修改login_qq函数的返回值可以获取cookies来登陆其他QQ的产品，如QQ邮箱等。


##QQ密码加密分析:

大部分加密可在如下网址中找到:
http://www.jianshu.com/p/4217d8f3574b
借用了里面的加密过程。可以直接用它里面的加密过程，并没有失效。
不过手动分析js时可能对他的加密方式有些疑问:
上面的网址分析里 密码的加密里的MD5里的盐有一个是用了QQ号作为盐，但是最新的c_login_2.js里没有用
到QQ号。现在的盐直接获取的是
```
https://ssl.ptlogin2.qq.com/check?xxx
```
这个请求里返回的一个值，不过返回的盐就是用QQ号做的盐，其他加密方法一致。

