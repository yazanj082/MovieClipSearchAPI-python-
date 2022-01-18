import re # used it to clean text from (<font>) header
import datetime
import os # used it to make the directory
import shutil # used it to delete directory tree
from datetime import datetime #used date time to manipulate time text
from moviepy.video.io.VideoFileClip import VideoFileClip
import pyodbc


query='insert into dbo.Clip(id,startTime,endTime,text,path) values(?,?,?,?,?)'
videoName = "The.Lego.Movie.2014.720p.BluRay.x264.YIFY.mp4 "#video file location
subtitleName = "Lego.srt" #subtitle file location



list=[] #will save subtitle file in list as lines

outfile=open("output.txt","w+",encoding="utf-8-sig")# opening output file in writing mode
outfile.write("")# making sure that the file is empty
outfile.close()
outfile=open("output.txt","a+",encoding="utf-8-sig")#opening output file in append mode
def conection():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=YAZANPC;'
                      'Database=Movie;'
                      'Trusted_Connection=yes;')
    return conn
con=conection()
cursor = con.cursor()
def mkodir(): # creating output videos folder
    directory = "output"

    # Parent Directory path
    parent_dir = os.getcwd()

    # Path
    path = os.path.join(parent_dir, directory)

    # Create the directory
    # 'output' in
    # 'current program directory'
    try:
        os.mkdir(path)
    except OSError as error: # if the directory exist delete it and then make new directory
        shutil.rmtree(path)
        os.mkdir(path)

def subclip(start, end, location): #video subcliping and saving
    with VideoFileClip(videoName) as video:
        if video.duration > start: #to make sure that he are in video range
            if video.duration < end : # the end time is bigger than video duration make it equal to video duration
                end= video.duration
            new=video.subclip(start,end)
            new.write_videofile(location, audio_codec='aac')


def Cformat(x): #changing time from string to int seconds

    fraction=x.split(",")
    fr=int(fraction[1])/1000
    time = datetime.strptime(x, '%H:%M:%S,%f') #time is date time object


    total_seconds = fr + time.second + time.minute * 60 + time.hour * 3600 #calculating the total seconds for given time

    return total_seconds

def process(number, duration, text):# making operations on lines we got from subtitle file(srt)
    TAG_RE = re.compile(r'<[^>]+>') # what simpol it will clean
    text=TAG_RE.sub('', text) # this function return the cleaned text
    time=duration.split(" ") # split start time from end time
    start=Cformat(time[0])# this is start time
    end=Cformat(time[2])# this is end time
    outfile.write(str(number)+"|"+str(start)+"|"+str(end)+"|"+str(text)+"|"+"/output/"+str(number)+".mp4\n")# outputing to text file
    cursor.execute(query, [number, (start), (end),str(text),"/output/"+str(number)+".mp4"])
    con.commit()
    subclip(start,end,"output/"+str(number)+".mp4")# called subclip function to cut the video into clips

mkodir() # called the function that will create the output folder for clips
file=open(subtitleName,encoding="utf-8-sig")# subtitle file


list = file.read().split("\n")#reading file and store it as lines in the list
file.close()


lineN=1 # for numbering each subclip subtitle(next target)

count=0# will increase with every loop
for line in list:
    if(str(lineN)==line): #searching for header number
        duration=list[count+1]# the time will always be next of header number
        text=""#here will store the text
        for index in range(count+2,count+10):#the text will be always the line after time
            if "</font>" in list[index]:#searching for the end of the text
                text += list[index]
                break#if i found the font end tag then break
            else:text+=list[index]#if didnt found the font end tag then add line and keep searching
        process(str(lineN),duration,text)#sending the data i collected to process function
        lineN+=1# incrementing the next target
    count+=1#increamenting the count
outfile.close()

