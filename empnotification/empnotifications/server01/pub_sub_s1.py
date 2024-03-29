import socket
import sys
import random

from _thread import *
from threading import Timer

userList = []
Employeetopics = ['Technology','Finance','Marketing','Human Resources','Design','Operations']
topics = ['Technology','Finance','Marketing']
subscriptions = {}
events = { 'Technology' : ['New artificial intelligence tool now available for data analysis', '5 reasons why you should use cloud computing in your business', 'Upcoming webinar on the latest trends in software development','How blockchain is revolutionizing supply chain management'],
    'Finance' : ['Stock market report: record highs for tech companies', 'How to make the most of your retirement savings','Upcoming conference on investment opportunities in emerging markets','The importance of financial planning for small businesses'],
    'Marketing' : ['How to create an effective social media marketing strategy','New trends in influencer marketing you need to know about','Upcoming conference on the future of digital marketing','The role of customer experience in brand loyalty']
}

generatedEvents = dict()
flags = dict()

def threadedClient(connection, data):
    while True:
        flags[data] = 0
        subscribe(data)
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions[data])
        connection.send(subscriptionInfo.encode())

        while True:
            if flags[data]==1:
                notify(connection,data)
    connection.close()

def threadedServerSender(connection, data):
    while True:
        flags[data] = 0
        subscriptions[data] = topics
        subscriptionInfo = 'Your subscriptions are : ' + str(subscriptions[data])
        connection.send(subscriptionInfo.encode())
        
        while True:
            if flags[data]==1:
                notify(connection,data)
    connection.close()

def threadedServerReceiver(connection, data):
    while True:
        serverData = connection.recv(2048).decode()
        m = serverData.split('-')
        if len(m)==2:
            topic = m[0]
            event = m[1]
            publish(topic,event,0)
    connection.close()

def subscribe(name):
    subscriptions[name] = ['Finance']


def eventGenerator():
    
    topic = random.choice(topics)
    msgList = events[topic]
    event = msgList[random.choice(list(range(1,len(msgList))))]
    
    publish(topic,event,1)


def publish(topic,event,indicator):
    
    event = topic + ' - ' + event
    
    if indicator == 1:
        for name, topics in subscriptions.items() :
            if topic in topics:
                if name in generatedEvents.keys():
                    generatedEvents[name].append(event)
                else:
                    generatedEvents.setdefault(name, []).append(event)
                flags[name] = 1

    else:
        for name, topics in subscriptions.items() :
            if name in userList: # only for clients
                if topic in topics:
                    if name in generatedEvents.keys():
                        generatedEvents[name].append(event)
                    else:
                        generatedEvents.setdefault(name, []).append(event)
                    flags[name] = 1

    t = Timer(random.choice(list(range(20,26))), eventGenerator)
    t.start()

                 
def notify(connection,name):
    if name in generatedEvents.keys():
        for msg in generatedEvents[name]:
            msg = msg  + str("\n")
            connection.send(msg.encode())
        del generatedEvents[name]
        flags[name] = 0

def Main():
    
    host = "" 
    port = 5040
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host,port))
    print("Socket is bind to the port :", port)
    s.listen(5)
    print("Socket is now listening for new connection ...")
    
    t = Timer(random.choice(list(range(20,26))), eventGenerator)
    t.start()
    
    while True:
        
        connection, addr = s.accept() 
        print('Connected to :', addr[0], ':', addr[1])
        data = connection.recv(2048).decode()

        if data:
            print("Welcome ", data)
        l = data.split('-')
        
        if l[0]=='c':
            userList.append(l[1])
            start_new_thread(threadedClient, (connection,l[1]))
        if l[0]=='s':
            start_new_thread(threadedServerSender, (connection,l[1]))
            start_new_thread(threadedServerReceiver, (connection,l[1]))

    s.close()

if __name__ == '__main__':
    Main() 
