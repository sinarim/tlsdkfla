import smtplib, email, poplib
from flask import Flask, render_template, request, url_for, redirect, flash, session
from email.message import EmailMessage
from email.mime.text import MIMEText
from datetime import datetime
from email.parser import BytesParser
from email import policy
import sqlite3


# SQLite 데이터베이스 연결
conn = sqlite3.connect('team02_06.db')
cursor = conn.cursor()

app = Flask(__name__)

app.secret_key = "qwer" 



@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
 
    if request.method == 'POST':
        user_name = request.form['name']
        user_pw = request.form['pwd']

        # SQLite 데이터베이스 연결
        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()

        # SQLite에서 사용자 확인
        cur.execute("SELECT * FROM users WHERE user_name = ? AND user_pw = ?", (user_name, user_pw))
        user = cur.fetchone()

        # 데이터베이스 연결 닫기
        conn.close()

        if user:
            session['logged_in'] = True
            session['username'] = user_name
            return redirect(url_for('send'))
        else:
            flash('로그인 실패!!!', 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html', error=error)

    
@app.route('/signGNK', methods=['GET','POST'])
def signGNK():
    error = None
    if request.method == 'POST':
        sign_user = request.form['user_id']
        sign_pwd = request.form['user_pw']
        sign_confirm = request.form['user_cp']

        # SQLite 데이터베이스 연결
        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()

        # SQLite에 사용자 추가
        cur.execute("INSERT INTO users (user_name, user_pw) VALUES (?, ?)", (sign_user, sign_pwd))
        conn.commit()

        # 추가된 사용자의 ID 가져오기
        cur.execute("SELECT user_id FROM users WHERE user_name = ? AND user_pw = ?", (sign_user, sign_pwd))
        user_id = cur.fetchone()

        # 데이터베이스 연결 닫기
        conn.close()

        session['user_id'] = user_id
        return render_template('signG.html')
    
    return render_template('signGNK.html', error=error)

@app.route('/signG', methods=['GET','POST'])
def signG():
    if request.method == 'POST':
        user_id = session['user_id']
        google_id = request.form['google_id']
        google_pw = request.form['google_pw']
        

        
        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()

     
        cur.execute("INSERT INTO usersEmail (user_id, google_name, google_pw) VALUES (?, ?, ?)", (user_id[0], google_id, google_pw))
        conn.commit()

      
        conn.close()

        return render_template('signN.html')
    
    return render_template("signG.html")

@app.route('/signN', methods=['POST'])
def signN():
    if request.method == 'POST':
        naver_id = request.form.get('naver_id')
        naver_pw = request.form['naver_pw']  # 수정: 'naver_id'가 아니라 'naver_pw'로 변경
        user_id = session['user_id']

       
        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()

      
        cur.execute("UPDATE usersEmail SET naver_name = ?, naver_pw = ? WHERE user_id = ?", (naver_id, naver_pw, user_id[0]))
        conn.commit()

       
        conn.close()

        return render_template('signK.html')

    return render_template('signN.html')


@app.route('/signK', methods=['POST'])
def signK():
    if request.method == 'POST':
        kakao_id = request.form['kakao_id']
        kakao_pw = request.form['kakao_pw']
        user_id = session['user_id']

        
        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()

       
        cur.execute("UPDATE usersEmail SET kakao_name = ?, kakao_pw = ? WHERE user_id = ?", (kakao_id, kakao_pw, user_id[0]))
        conn.commit()

       
        conn.close()

        session.pop('user_id', None)
        return render_template('login.html')

    return render_template('signK.html')


@app.route('/write11', methods=['POST'])
def write11():
    if request.method == 'POST':
        user_name = session['username']
        subject = request.form['subject']
        message = request.form['message']
        recipient = request.form['recipient']
        option = request.form['option']

        SMTP_SERVER = getSmtpServer(option)
        SMTP_PORT = 465  # SSL
        EMAIL_ADDR = 'asdf1472486@gmail.com'  # 연동 Email
        EMAIL_PASSWORD = 'xxmi rifl vtut qyez'  # 비번

    # SMTP 서버 연결
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

    # SMTP 서버에 로그인
        smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

    # MIME 형태의 이메일 메세지 작성
        msg = EmailMessage()
        msg["Subject"] = subject  # 메일 제목
        msg["From"] = EMAIL_ADDR  # 보내는 사람
        msg["To"] = recipient  # 받는 사람 db에 저장할지 생각 중
        msg.set_content(message)  # 전송 내용

    # 서버로 메일 보내기
        smtp.send_message(msg)

    # 메일을 보내면 서버와의 연결 끊기
        smtp.quit()

        conn = sqlite3.connect('team02_06.db')
        cur = conn.cursor()
        
    # SMTP 정보 데이터베이스에 추가
        cur.execute("INSERT INTO smtp (smtp_user, smtp_subject, smtp_recipient, smtp_message) VALUES (?, ?, ?, ?)", (EMAIL_ADDR, subject, recipient, message))
        cur.connection.commit()
        
        smtpdata = cur.fetchall()
        conn.close()

        return render_template('send.html', smtpdata=smtpdata)

    return render_template('write.html')
   
    



def getSmtpServer(option):
    if option == 'google':
        return 'smtp.gmail.com'
    elif option == 'naver':
        return 'smtp.naver.com'
    elif option == 'kakao':
        return 'smtp.kakao.com'

    


def send_email(subject, message, recipient, option, cur, user_name):
    # 이메일 설정
    SMTP_SERVER = getSmtpServer(option)
    SMTP_PORT = 465  # SSL
    EMAIL_ADDR = 'asdf1472486@gmail.com'  # 연동 Email
    EMAIL_PASSWORD = 'xxmi rifl vtut qyez'  # 비번

    # SMTP 서버 연결
    smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

    # SMTP 서버에 로그인
    smtp.login(EMAIL_ADDR, EMAIL_PASSWORD)

    # MIME 형태의 이메일 메세지 작성
    msg = EmailMessage()
    msg["Subject"] = subject  # 메일 제목
    msg["From"] = EMAIL_ADDR  # 보내는 사람
    msg["To"] = recipient  # 받는 사람 db에 저장할지 생각 중
    msg.set_content(message)  # 전송 내용

    # 서버로 메일 보내기
    smtp.send_message(msg)

    # 메일을 보내면 서버와의 연결 끊기
    smtp.quit()

    # SMTP 정보 데이터베이스에 추가
    cur.execute("INSERT INTO smtp (smtp_user, smtp_subject, smtp_recipient, smtp_message) VALUES (?, ?, ?, ?)",
                (EMAIL_ADDR, subject, recipient, message))
    cur.execute("SELECT * FROM smtp")
    smtpdata = cur.fetchall()

    # 데이터베이스 커밋
    cur.connection.commit()

    return smtpdata

def getSmtpServer(option):
    if option == 'google':
        return 'smtp.gmail.com'
    elif option == 'naver':
        return 'smtp.naver.com'
    elif option == 'kakao':
        return 'smtp.kakao.com'


@app.route('/signup')
def signup():
    return render_template("signGNK.html")

@app.route('/write')
def write():
    return render_template('write.html')

@app.route('/receive')
def receive():
    return render_template("receive.html")


@app.route('/writeme')
def writeme():
    return render_template('writeme.html')

@app.route('/writemegather')
def writemegather():
    return render_template('writemegather.html')

@app.route('/trash')
def trash():
    return render_template('trash.html')
    
@app.route('/send')
def send():
    return render_template('send.html')

if __name__ == "__main__": 
        
    app.run(debug=True, host='0.0.0.0', port=5000)


