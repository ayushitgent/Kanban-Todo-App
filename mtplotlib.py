import matplotlib.pyplot as plt
from collections import OrderedDict
from app import db, User, Task_lis

def genplot(id):
    t1=Task_lis.query.filter_by(list_id=id).first()
    q={}
    for card in t1.card_rel:
        if card.deadline in q:
            q[card.deadline]+=1
        else:
            q[card.deadline]=1
    dict1 = dict(OrderedDict(sorted(q.items())))
    deadlines=dict1.keys()
    tasks=dict1.values()

    fig = plt.figure(figsize = (10, 7))

    # creating the bar plot
    plt.bar(deadlines, tasks, color ='maroon',
        width = 0.4)

    plt.xlabel("Courses offered")
    plt.ylabel("No. of tasks")
    plt.title("Deadline")
    plt.xticks(rotation=45)
    plt.savefig(f'static/list_bar{t1.list_id}.png')

u1=User.query.filter_by(name='Gokul').first()
for list in u1.tasks_rel:
    id=list.list_id
    genplot(id)