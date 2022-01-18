import os

import spacy # used spacy for comparing text and getting similarity
import pyodbc
from flask import Flask, request, send_file
from flask_restful import Resource, Api
domain="127.0.0.1"
app=Flask("BackEndApp")


def conection():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=YAZANPC;'
                      'Database=Movie;'
                      'Trusted_Connection=yes;')
    return conn

con=conection()
cursor = con.cursor()

nlp = spacy.load("en_core_web_lg") # loading spacy moodle large

def search(s):
    doc2=nlp(s) # passing user string to spacy object


    query='select * from dbo.Clip'
    query1='select * from dbo.Clip where id=?'

    cursor.execute(query)


    max=0 # will store in it max similarity
    maxnumber=0 # will store in it the item number that has the highist similarity
    for row in cursor:
        doc = nlp(row[3])
        if (doc.vector_norm):  # checking if the text is valid
            sim = doc.similarity(doc2)
        else:
            sim = 0
        if sim > max:
            max = sim
            maxnumber = row[0]
            if(sim == 1):
                break


    cursor.execute(query1,maxnumber)

    target= cursor.fetchone() # storing the highest similarity item in target list then printing it
    return target


def Tsearch(start,end):
    query = 'select * from dbo.Clip where startTime >= ? and endTime <= ?'
    cursor.execute(query,[start,end])
    list1= []
    for row in cursor:
        target=row
        output = "("
        output += "clip number : " + str(target[0])
        output += ",clip start time (in seconds) : " + str(target[1])
        output += ",clip end time (in seconds) : " + str(target[2])
        output += ",clip text : " + target[3]
        output += ",clip url : " + "http://" + domain + ":8888/Stream?name=" + target[4].split("/")[2]
        output += ")"
        list1.append(output)
    return list1





class UserSearch(Resource):
    def get(self):
        s=request.args.get("input")
        target=search(s)
        output="("
        output+="clip number : " + str(target[0])
        output+=",clip start time (in seconds) : " + str(target[1])
        output+=",clip end time (in seconds) : " + str(target[2])
        output+=",clip text : " + target[3]
        output+=",clip url : " +"http://"+domain+":8888/Stream?name="+target[4].split("/")[2]
        output+=")"

        return (output)
class Stream(Resource):
    def get(self):
        name=request.args.get("name")

        return send_file("output/"+name,mimetype="video/mp4")
class ClipSearch(Resource):
    def get(self):
        start = request.args.get("UserStartTime")
        end = request.args.get("UserEndTime")
        return Tsearch(float(start),float(end))


api = Api(app)
api.add_resource(UserSearch,"/UserSearch")
api.add_resource(ClipSearch,"/ClipSearch")
api.add_resource(Stream,"/Stream")
app.run(port=8888,host=domain)