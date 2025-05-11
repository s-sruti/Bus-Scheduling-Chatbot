# utils/intent_detector.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
# from transformers import pipeline
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
# Load a small model (good enough for intent detection)
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")



class IntentDetector:
    def __init__(self, example_file):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.examples = []
        self.labels = []
        self.embeddings = []
        self.reply=[]
        self.load_examples(example_file)

    def load_examples(self, example_file):
        with open(example_file, 'r' ,encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                self.examples.append(item['query'])
                self.labels.append(item['intent'])
                self.reply.append(item['response_template'])
            self.embeddings = self.model.encode(self.examples)

    def detect_intent(self, user_input):
        user_embedding = self.model.encode([user_input])
        similarities = cosine_similarity(user_embedding, self.embeddings)[0]
        max_index = similarities.argmax()
        max_score = similarities[max_index]
        print(max_score,self.reply[max_index])
        if max_score >= 0.6:  # Threshold for understanding
            return max_index,self.labels[max_index]
        else:
            return "Cant understand","unknown"

def entities_detect_schedule(location,user_input):
    
    if location is None :
        source=re.findall("(?:in |from |at |is |of )([a-z,A-Z]+)",user_input)
        if source:
            location=source[0]
    if location is None :
        return "Can you tell me the location?", location
    else:
        return  f"Todays schedule for the current location {location} is given below\n",location


def entities_detect_map(user_input,session_data):
    
    if session_data['source'] is None :
        source=re.findall("from ([a-z,A-Z]+)",user_input)
        print(source)
        if source:
            print(source)
            session_data['source']=source[0].lower()
    if session_data['destination'] is None :
        destination=re.findall("to ([a-z,A-Z]+)",user_input)
        if destination:
            print(destination)
            session_data['destination']=destination[0].lower()
    if session_data['source'] is None:
        return "Can you tell me from where you want to travel?", session_data
    elif session_data['destination'] is None:
        return "Can you tell me your destination?", session_data
    else:
        return  "Currently, I can't retrieve the detailed info. You can check it directly by clicking the link below!",session_data

def entities_detect(user_input,session_data):
    if session_data['source'] is None :
        source=re.findall("from ([a-z,A-Z]+)",user_input)
        print(source)
        if source:
            print(source)
            session_data['source']=source[0]
    if session_data['destination'] is None :
        destination=re.findall("to ([a-z,A-Z]+)",user_input)
        if destination:
            print(destination)
            session_data['destination']=destination[0]
    if session_data['date'] is None:
        pattern = r"\b\d{1,2}([/-]\d{1,2}([/-]\d{2,4})?| [a-zA-Z]{3,9}( \d{2,4})?)\b"
        matches = re.finditer(pattern, user_input)
        
        formatted_dates = []
        current_year = datetime.now().year
        
        for match in matches:
            date_str = match.group()
            try:
                # Handle 24/09/2015 or 24-9-2025
                if "/" in date_str or "-" in date_str:
                    sep = "/" if "/" in date_str else "-"
                    parts = date_str.split(sep)
                    if len(parts) == 2:
                        # Only day and month provided
                        day, month = parts
                        year = current_year
                    elif len(parts) == 3:
                        day, month, year = parts
                    else:
                        continue  # Invalid, skip
                    
                    # Normalize all parts to integers
                    day, month, year = int(day), int(month), int(year)
                    if year < 100:  # Handle two-digit years
                        year += 2000
                    date_obj = datetime(year, month, day)
                
                # Handle 24 sep, 28 sep 2026
                elif " " in date_str:
                    parts = date_str.split()
                    day = int(parts[0])
                    month_str = parts[1]
                    month = datetime.strptime(month_str[:3], "%b").month  # Parse month name
                    if len(parts) == 3:
                        year = int(parts[2])
                    else:
                        year = current_year
                    date_obj = datetime(year, month, day)
                else:
                    continue  # Invalid format, skip

                # Convert to YYYY-MM-DD
                formatted_dates.append(date_obj.strftime("%Y-%m-%d"))
                date=formatted_dates[0]
                if date:
                    session_data['date']=date
            except Exception as e:
                print(f"Skipping invalid date format: {date_str}. Error: {e}")
                continue

   

    if session_data['source'] is None:
        return "Can you tell me from where you want to travel?", session_data
    elif session_data['destination'] is None:
        return "Can you tell me your destination?", session_data
    elif session_data['date'] is None:
        return "Can you tell me your travel date?", session_data
    else:
        res=" yes let me return the available buses from {} to {} on {}".format(session_data['source'],session_data['destination'],session_data['date'])
        return res,session_data



def schedule(location):
    
    url="https://msrtcbooking.in/station/{}/".format(location['source'])
    response = requests.get(url)
    response.raise_for_status()
    message=[]
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the bus cards
    cards = soup.find_all('div', class_="bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden transform hover:shadow-xl transition-transform duration-300")
    # cards[:]=cards[:10]
    for card in cards:
        try:
            # Extract Route
            route = card.find('h4').get_text(separator=" ", strip=True)
            s=f"{location['source'].title()} ([a-z,A-Z]+)"
            val=re.findall(s,route)
           
            if re.findall(s,route)[0]!=location['destination'].title():
                continue
            # Extract Departure Time
            departure_tag = card.find('strong', string="Departure:")
            departure_time = departure_tag.find_next('span').text.strip() if departure_tag else 'N/A'
            if departure_time=='N/A':
                continue
            # Extract Price
            price_tag = card.find('strong', string="Price:")
            price = price_tag.find_next('span').text.strip() if price_tag else 'N/A'

            # Extract Stops
            # stops_div = card.find('div', class_="mt-1 text-sm text-gray-800 dark:text-gray-100")
            # stops = stops_div.get_text(separator=" ", strip=True) if stops_div else 'No stops info'

            # Format and print nicely
            message.append( f"""🚌 Route: {route}\n⏰ Departure: {departure_time}\n💵 Price: ₹{price}""")
            
    
            
        except Exception as e:
            print(f"Error parsing card: {e}")
    
    message[:]=message[:13]
    return "\n".join(message)

session_data_map={
            "source":'kolhapur',
            "destination":'swargate'
            }
res=schedule(session_data_map)



