from flask import Flask, render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_session import Session
import matplotlib.pyplot as plt
from collections import OrderedDict
import os



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
IMG_FOLDER = os.path.join('static', 'images')

app.config['UPLOAD_FOLDER'] = IMG_FOLDER

Session(app)
db=SQLAlchemy(app)



class User(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(20))
    email = db.Column(db.String(30))
    occupation = db.Column(db.String(20))
    contactno= db.Column(db.Integer)
    password=db.Column(db.String(20))
    tasksrel=db.relationship('Task_lis',backref='user')
    
class Task_lis(db.Model):
    listid=db.Column(db.Integer,primary_key=True,autoincrement=True)
    listname=db.Column(db.String(20))
    userid=db.Column(db.Integer,db.ForeignKey('user.id'))
    cardrel=db.relationship('Card',backref="task_lis")
    
class Card(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    title=db.Column(db.String(20))
    content=db.Column(db.String())
    created = db.Column(db.DateTime, default=datetime.utcnow)
    iscompleted=db.Column(db.String(5),default=False,nullable=False)
    completiontime=db.Column(db.String())
    taskid=db.Column(db.Integer,db.ForeignKey('task_lis.listid'))

data={}
@app.route('/')
def login(): 
    return render_template("index.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/profile')
def profile(): 
    username = session.get("username")
    temp =User.query.filter_by(username=username).first()
    data["user"] = temp
    return render_template("profile.html",data=data)

@app.route('/dashboard', methods = ["GET","POST"])
def dashboard():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        username = session.get("username")
        temp =User.query.filter_by(username=username,password=password).first()
        if not temp:
            return "UserName or Passwaord is incorrect ! New User ? Please sign Up "           
        data['user']= temp  
        return render_template("dashboard.html",data=data)
    else:
        username = session.get("username")
        temp =User.query.filter_by(username=username).first()
        data['user']= temp  
        return render_template("dashboard.html",data=data)
    
@app.route('/dashboard2', methods = ["GET","POST"])
def dashboard2():
    if request.method=="POST":
        username = request.form["username"]
        email = request.form["email"]
        occupation = request.form["occupation"]
        contactno = request.form["contactno"]
        password = request.form["password"]
        #username = session.get("username")
        temp =User.query.filter_by(username=username,password=password).first()
        if temp:
            return "User Already Exists! Please Login !"  
        temp=User(username=username,password=password,contactno=contactno,occupation=occupation,email=email)
        db.session.add(temp)
        db.session.commit()
        data["user"] = temp 
        return render_template("dashboard.html",data=data)
    return "NONE"

@app.route('/add_list', methods = ["GET","POST"])
def add_list():
    if request.method =="POST":
        username = session.get("username")
        listname = request.form['listname']
        temp=User.query.filter_by(username=username).first()
        list=Task_lis(listname=listname,userid = temp.id)
        db.session.add(list)
        db.session.commit()
        data["user"] = temp
        return render_template('dashboard.html',data = data)
    else:
        return render_template('add_list.html')

@app.route('/add_card/<listname>', methods=['GET','POST'])
def add_card(listname):
    if request.method=='POST':
        cardname=request.form['card_name']
        cardcontent=request.form['card_content']
        cardstatus=request.form['card_status']
        carddeadline=request.form['card_deadline']
        username=session.get('username')
        taskid=Task_lis.query.filter_by(listname=listname).first().listid
        card=Card(title=cardname, content=cardcontent, iscompleted=cardstatus, completiontime=carddeadline, taskid=taskid)
        db.session.add(card)
        db.session.commit()
        cuser=User.query.filter_by(username=username).first()
        data['user']=cuser
        return render_template('dashboard.html', data=data)
    return render_template('add_card.html', data=data,listname=listname)



@app.route('/edit/list/<listid>', methods=['GET','POST'])
def edit_list(listid):
    if request.method=='POST':
        list=Task_lis.query.filter_by(listid=listid).first()
        new_listname=request.form['listname']
        list.listname=new_listname
        current_db_sessions = db.session.object_session(list)
        current_db_sessions.add(list)
        current_db_sessions.commit()
        username=session.get('username')
        temp=User.query.filter_by(username=username).first()
        data['user']=temp
        return render_template('dashboard.html', data=data)
    else:
        list=Task_lis.query.filter_by(listid=listid).first()
        return render_template('edit_list.html', list=list)


@app.route('/edit/card/<id>', methods=['GET','POST'])
def edit_card(id):
    if request.method=='POST':
        card=Card.query.filter_by(id=id).first()
        card.title=request.form['card_name']
        card.content=request.form['card_content']
        card.iscompleted=request.form['card_status']
        card.completiontime=request.form['card_deadline']
        taskname=request.form['taskname']
        card.taskid=Task_lis.query.filter_by(listid=taskname).first().listid
        current_db_sessions = db.session.object_session(card)
        current_db_sessions.add(card)
        current_db_sessions.commit()
        username=session.get('username')
        temp=User.query.filter_by(username=username).first()
        data['user']=temp
        return render_template('dashboard.html', data=data)
    else:
        card=Card.query.filter_by(id=id).first()
        username=session.get('username')
        temp=User.query.filter_by(username=username).first()
        data['user']=temp
        return render_template('edit_card.html', card=card, data=data)

def genplot(id):
    t1=Task_lis.query.filter_by(listid=id).first()
    deaddict={}
    for card in t1.cardrel:
        if card.completiontime in deaddict:
            deaddict[card.completiontime]+=1
        else:
            deaddict[card.completiontime]=1
    dict1 = dict(OrderedDict(sorted(deaddict.items())))
    deadlinelist=dict1.keys()
    tasklist=dict1.values()

    fig = plt.figure(figsize = (10, 7))

    # creating the bar plot
    plt.bar(deadlinelist, tasklist, color ='maroon',
        width = 0.4)

    plt.xlabel("Courses offered")
    plt.ylabel("No. of tasks")
    plt.title("Deadline")
    plt.xticks(rotation=45)
    plt.savefig(f'static/images/list_bargraph{t1.listid}.png')

@app.route('/summary', methods=['GET','POST'])
def summary():
    username=session.get('username')
    userlists=User.query.filter_by(username=username).first()
    completeddict={}
    listname = {}
    deadlinepasseddict={}
    total={}
    for i in userlists.tasksrel:
        total[i.listid]=len(i.cardrel)
        deadlinepasseddict[i.listid]=0
        listname[i.listid] = i.listname 
        count=0
        for card in i.cardrel:
            currenttime=datetime.utcnow()
            if int(card.completiontime[:4])<=currenttime.year and int(card.completiontime[5:7])<=currenttime.month and int(card.completiontime[8:10])<currenttime.day:
                deadlinepasseddict[i.listid]+=1
            if card.iscompleted=='True':
                count=count+1
        completeddict[i.listid]=count
    img_dic={}    
    listids=[]
    
    for i in userlists.tasksrel:
        img_dic[i.listid]=os.path.join(app.config['UPLOAD_FOLDER'], f'list_bargraph{i.listid}.png')
        listids.append(i.listid)
    Flask_Logo = img_dic
    # img_dic={1: '.\static\images\list_bar1.png', 2: 'static\images\list_bar2.png', 3: 'static\images\list_bar3.png'}
    dic={}
    for i in userlists.tasksrel:
        dic[i.listid]='\\'+str(os.path.join(app.config['UPLOAD_FOLDER'], f'list_bargraph{i.listid}.png'))
    print(dic)
    Flask_Logo = dic
    listids=completeddict.keys()
    print(listids)
    for k in listids:
        genplot(k)
    return render_template('summary.html',username = username,name = listname, data=data, completed=completeddict, total=total, deadline_passed=deadlinepasseddict,image_bar=img_dic,list_id=listids,user_image=Flask_Logo)

@app.route("/1")
def rou():
    userlists=User.query.filter_by(name="Yash").first()
    dic={}
    for i in range(1,4):
        dic[i]=os.path.join(app.config['UPLOAD_FOLDER'], f'list_bar{i}.png')
    Flask_Logo = dic
    completed={}
    deadline_passed={}
    Total={}
    for i in userlists.tasks_rel:
        Total[i.list_id]=len(i.card_rel)
        deadline_passed[i.list_id]=0
        count=0
        for card in i.card_rel:
            ctime=datetime.now()
            if int(card.deadline[:4])<=ctime.year and int(card.deadline[5:7])<=ctime.month and int(card.deadline[8:10])<ctime.day:
                deadline_passed[i.list_id]+=1
            if card.is_completed=='True':
                count=count+1
        completed[i.list_id]=count
        id=[1,2,3,4,7]
    return render_template("index1.html", user_image=Flask_Logo,completed=completed, total=Total, deadline_passed=deadline_passed,list=id)
  
@app.route('/delete/list/<listid>', methods=['GET'])
def deletelist(listid):
    id=Task_lis.query.filter_by(listid=listid).first()
    current_db_sessions = db.session.object_session(id)
    current_db_sessions.delete(id)
    current_db_sessions.commit()
    username=session.get('username')
    temp=User.query.filter_by(username=username).first()
    data['user']=temp
    return render_template('dashboard.html', data=data)

@app.route('/delete/card/<id>', methods=['GET','POST'])
def deletecard(id):
    card=Card.query.filter_by(id=id).first()
    current_db_sessions = db.session.object_session(card)
    current_db_sessions.delete(card)
    current_db_sessions.commit()
    username=session.get('username')
    temp=User.query.filter_by(username=username).first()
    data['user']=temp
    return render_template('dashboard.html', data=data)

from api import *
if __name__ == "__main__":
    db.create_all()
    app.run(debug = True,port=1000)


