from langchain_groq import ChatGroq
from pymongo import MongoClient
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
import requests
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()
llm=ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv('GROQ_API_KEY'))
chain=ChatPromptTemplate.from_template(template="You are an ai that fetches the city name for the zip/postal code provided by the user, your answer should be only one word the city name and if city name or coordinates are given to you dont do anything and return them as it is. The input is: {input}") | llm

client=MongoClient(os.getenv('DB_KEY'))
db=client['Weather_app']
collection=db["Weather_info"]

def get_weather():
    location_input=str(input("Enter zip/postal code, city name or coordinates: "))
    resp=chain.invoke({"input":location_input})
    location=resp.content
    start_date=str(input("Enter start date (ex: 06-08-26): "))
    end_date=str(input("Enter end date (ex: 10-08-26): "))
    api_key=os.getenv('WEATHER_API_KEY')
    base_url="https://api.openweathermap.org/data/2.5/weather"
    parameters={
        'appid':api_key,
        'units':"metric",
        'mode':"json"
    }
    start=datetime.strptime(start_date,"%d-%m-%y")
    end=datetime.strptime(end_date,"%d-%m-%y")
    duration=(end-start).days
    if duration>5:
        print("Enter date within 5 days duration")
    else:
        parameters['cnt']=duration*8
    if "," in location:
        try:
            lat,lon= location.split(",")
            parameters["lat"]=lat.strip()
            parameters["lon"]=lon.strip()
        except ValueError:
            print("Invalid coordinates")
    else:
        parameters['q']=location
    try:
        req=requests.get(url=base_url,params=parameters)
        req.raise_for_status()
        response=req.json()
        try:
            parameters2={
                'q':f"{response['name']} in {response['weather'][0]['description']} weather city tour",
                'part':'snippet',
                'type':'video',
                'maxResults':5,
                'key':os.getenv('YT_API_KEY')
            }
            request2=requests.get('https://www.googleapis.com/youtube/v3/search',params=parameters2)
            request2.raise_for_status()
            response2=request2.json()
            print(f"These below are video links of how {response['name']} looks like in {response['weather'][0]['description']} weather")
            for item in response2.get('items', []):
                if item.get('id', {}).get('kind') == 'youtube#video':
                    video_id = item['id']['videoId']
                    print(f"https://www.youtube.com/watch?v={video_id}")
        except requests.exceptions.HTTPError as code:
            if request2.status_code==400:
                print("Bad request")
            elif request2.status_code==429:
                print("Limit exceeded")
            elif request2.status_code==401:
                print("Error in api key")
            else:
                print(code)        
        output={
            'city':response['name'],
            'country':response['sys']['country'],
            'weather':response['weather'][0]['description'],
            'temprature':f"{response['main']['temp']}°C",
            'feels like':f"{response['main']['feels_like']}°C",
            'pressure':f"{response['main']['pressure']}mb",
            'humidity':f"{response['main']['humidity']}%",
            'wind speed':f"{response['wind']['speed']}m/s",
            'start_date':start,
            'end_date':end
        }
        result=collection.insert_one(output)
        return str(result.inserted_id)
    except requests.exceptions.HTTPError as http_err:
        if req.status_code == 404:
            print("Error: City not found. Please check the spelling.")
        elif req.status_code == 401:
            print("Error: Invalid API key. Ensure your key is active.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}") 

def read_db(query_id=None):
    if query_id:
        res=collection.find({"_id":ObjectId(query_id)})
        return list(res)
    else:
        return list(collection.find())

def update_db(query_id,start_new,end_new):
    res=collection.update_one({'_id':ObjectId(query_id)},{'$set':{'start_date':start_new,'end_date':end_new}})

def del_db(query_id=None):
    if query_id:
        res=collection.delete_one({'_id':ObjectId(query_id)})
    else:
        res=collection.delete_many({})

def export_to_csv():
    try:
        cursor=collection.find()
        docs=list(cursor)
        if not docs:
            print("No file in database to export")
            return
        df=pd.DataFrame(docs)
        if '_id' in df.columns:
            df['_id']=df['_id'].astype(str)
            df=df.drop(columns=['_id'])
        df.to_csv("exported_file.csv",index=False)
    except Exception as e:
        print(e)

def about():
    print("Weather Forecast App")
    print("Built by Somya Tiwari")
    print("Created for PM Accelerator's technical assessment")
    print("The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.

Our Product Manager Accelerator community are ambitious and committed. Through our program they have learnt, honed and developed new PM and leadership skills, giving them a strong foundation for their future endeavors.

Here are the examples of services we offer. Check out our website https://www.pmaccelerator.io/ to learn more about our services.

🚀 PMA Pro
End-to-end product manager job hunting program that helps you master FAANG-level Product Management skills, conduct unlimited mock interviews, and gain job referrals through our largest alumni network. 25% of our offers came from tier 1 companies and get paid as high as $800K/year. 

🚀 AI PM Bootcamp
Gain hands-on AI Product Management skills by building a real-life AI product with a team of AI Engineers, data scientists, and designers. We will also help you launch your product with real user engagement using our 100,000+ PM community and social media channels. 

🚀 PMA Power Skills
Designed for existing product managers to sharpen their product management skills, leadership skills, and executive presentation skills

🚀 PMA Leader
We help you accelerate your product management career, get promoted to Director and product executive levels, and win in the board room. 

🚀 1:1 Resume Review
We help you rewrite your killer product manager resume to stand out from the crowd, with an interview guarantee.  Get started by using our FREE killer PM resume template used by over 14,000 product managers. https://www.drnancyli.com/pmresume

🚀 We also published over 500+ free training and courses. Please go to my YouTube channel https://www.youtube.com/c/drnancyli and Instagram @drnancyli to start learning for free today.")
    print("LinkedIn: https://www.linkedin.com/company/pmaccelerator/")
