import crypt
import datetime
import hashlib
import os
import spwd
from flask import Flask, redirect, request, render_template, send_file, session, url_for

app = Flask(__name__)

def searchUser(username,password):
   
    try:
        # Get the user's encrypted password from /etc/shadow
        hashed_pw = spwd.getspnam(username).sp_pwd # type: ignore
        # Encrypt the provided password using the same salt as the stored password
        salt = hashed_pw[:hashed_pw.index("$", 3) + 1]
        encrypted_pw = crypt.crypt(password, salt)
        # Compare the encrypted password with the stored password
        if encrypted_pw == hashed_pw:
            print(f"User {username} authenticated successfully")
            return True
        else:
            print(f"Invalid username or password")
            return False
    except KeyError:
        print(f"User {username} not found in /etc/shadow")
        return False
    
def generate_key(login):
    return hashlib.md5(str(login).encode('utf-8')).hexdigest()

def getDirectories():
    home = os.path.expanduser("~")
    directories = {}
    for filename in os.listdir(home):
        if os.path.isdir(os.path.join(home, filename)):
            path = os.path.join(home, filename)
            directories[filename] = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return directories

def getFileCount():
    home = os.path.expanduser("~")
    file_count = 0
    for _, _, files in os.walk(home):
        file_count += len(files)
    return file_count

def getDirCount():
    home = os.path.expanduser("~")
    dir_count = 0
    for _, dirs, _ in os.walk(home):
        dir_count += len(dirs)
    return dir_count

def getSpaceUsage():
    home = os.path.expanduser("~")
    total, used, free = os.statvfs(home)[0:3]
    space_usage = (total - free) / float(total)
    return space_usage

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    if searchUser(username,password):
        app.secret_key=generate_key(username)
        session['user_id']=username  
        directories = getDirectories()
        file_count = getFileCount()
        dir_count = getDirCount()
        space_usage = getSpaceUsage()
        return render_template('index.html', directories=directories, file_count=file_count, dir_count=dir_count, space_usage=space_usage)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return render_template('login.html')


@app.route('/download_home')
def download_home():
    user_home_dir = os.path.expanduser('~')
    zip_filename = 'home.zip'
    # Create a ZIP file of the user's home directory
    os.system(f'zip -r {zip_filename} {user_home_dir}')
    # Send the ZIP file as a response to the client
    return send_file(zip_filename, as_attachment=True)
if __name__ == '__main__':
    app.secret_key='1233'
    app.run(host="0.0.0.0",port=9090,debug=True)
