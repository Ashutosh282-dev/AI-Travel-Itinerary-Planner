import streamlit as st
import requests
import random
from datetime import date

# ---------------- Dynamic Fallback Generation ---------------- #

def generate_dynamic_fallback(destination, count):
    """
    Generates 'count' unique fallback tasks for the given destination 
    using a variety of templates and adjectives.
    """
    templates = [
        "Explore local art galleries in {}",
        "Attend a live music concert in {}",
        "Experience a local music festival in {}",
        "Relax in a scenic park in {}",
        "Visit a quirky museum in {}",
        "Discover historical heritage at a museum in {}",
        "Shop at local markets in {}",
        "Browse boutique shops in {}",
        "Join a guided historical tour in {}",
        "Take a local cooking class in {}",
        "Discover hidden alleys in {}",
        "Stroll along the coastline in {}",
        "Enjoy an evening cruise in {}",
        "Attend an art exhibition in {}",
        "Join a street art tour in {}",
        "Visit an open-air festival in {}",
        "Savor regional street food in {}",
        "Take a bicycle tour in {}",
        "Join a cultural workshop in {}",
        "Discover local handicrafts in {}"
    ]
    adjectives = ["amazing", "unforgettable", "charming", "historic", 
                  "vibrant", "quaint", "dynamic", "bustling", "splendid", 
                  "exciting", "remarkable"]
    fallbacks = set()
    attempts = 0
    while len(fallbacks) < count and attempts < count * 10:
        tpl = random.choice(templates)
        prefix = (random.choice(adjectives) + " ") if random.random() < 0.6 else ""
        fallback_item = tpl.format(prefix + destination)
        fallbacks.add(fallback_item)
        attempts += 1
    return list(fallbacks)

def get_fallback_list(destination):
    """
    Returns a fallback pool with 50 unique fallback tasks for the destination.
    """
    return generate_dynamic_fallback(destination, 50)

# ------------------ Helper Functions ------------------ #

def split_list(lst, n):
    """Splits list 'lst' into n nearly equal parts."""
    if n <= 0:
        return []
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def create_global_pool(tasks, fallback_list, destination, required):
    """
    Builds a global pool by removing duplicates from tasks and adding fallback items 
    until we have at least 'required' unique items.
    """
    unique_tasks = []
    for task in tasks:
        if task not in unique_tasks:
            unique_tasks.append(task)
    while len(unique_tasks) < required:
        candidate = fallback_list[random.randrange(len(fallback_list))]
        if candidate not in unique_tasks:
            unique_tasks.append(candidate)
    return unique_tasks

def generate_groups_from_global_pool(global_pool, days, tasks_per_day):
    """
    Randomly samples exactly days*tasks_per_day tasks from the global pool (without replacement)
    and splits them into groups of tasks_per_day.
    """
    required = days * tasks_per_day
    sampled_tasks = random.sample(global_pool, required)
    groups = [sampled_tasks[i * tasks_per_day:(i + 1) * tasks_per_day] for i in range(days)]
    return groups

def fetch_itinerary_from_wiki(destination, duration):
    """
    Uses Wikipedia's opensearch API to fetch tourist attraction suggestions 
    for a custom destination. After deduplication and augmentation with fallback items,
    it ensures there are at least (duration * 3) unique items and splits them into daily groups.
    """
    points_required = duration * 3  
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": f"{destination} tourist attractions",
        "limit": points_required,
        "namespace": 0,
        "format": "json"
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        tasks = data[1]  # suggestion list
        
        unique_tasks = []
        for t in tasks:
            if t not in unique_tasks:
                unique_tasks.append(t)
        tasks = unique_tasks
        
        fallback_list = get_fallback_list(destination)
        global_pool = create_global_pool(tasks, fallback_list, destination, points_required)
        groups = generate_groups_from_global_pool(global_pool, duration, 3)
        itinerary = [{"Day": i + 1, "Activities": group} for i, group in enumerate(groups)]
        return itinerary
    except Exception as e:
        st.error("Error fetching live itinerary: " + str(e))
        return []

def get_travel_advice(destination, travel_date):
    """
    Returns weather advice (based on the month) and language tips for the destination.
    Provides specific advice for preset destinations and generic messages for others.
    """
    month = travel_date.month
    month_name = travel_date.strftime("%B")
    if destination == "Paris":
        if month in [12, 1, 2]:
            weather = f"In {month_name}, Paris is wintry (around 5-10°C) – pack heavy, warm clothing."
        elif month in [3, 4, 5]:
            weather = f"In {month_name}, Paris enjoys mild spring weather (10-15°C) with occasional rain – bring a light jacket and umbrella."
        elif month in [6, 7, 8]:
            weather = f"In {month_name}, Paris is pleasantly warm (20-25°C) though evenings can be cool – opt for light clothing and a sweater."
        else:
            weather = f"In {month_name}, Paris is cool and sometimes rainy (10-15°C) – layering is advisable."
        language = "French is the official language. Basic phrases like 'Bonjour', 'Merci', and 'Au revoir' are very useful."
    elif destination == "Tokyo":
        if month in [12, 1, 2]:
            weather = f"During {month_name}, Tokyo can be chilly (5-10°C) – pack warm layers."
        elif month in [3, 4, 5]:
            weather = f"In {month_name}, Tokyo enjoys mild weather (10-18°C) with some rain – dress in layers and carry an umbrella."
        elif month in [6, 7, 8]:
            weather = f"In {month_name}, Tokyo is hot and humid (25-30°C) – wear light, breathable clothing and use sunscreen."
        else:
            weather = f"In {month_name}, Tokyo's weather is mild with occasional showers (15-20°C) – a light jacket is sufficient."
        language = "Japanese is the primary language. Learning phrases like 'こんにちは (Konnichiwa)' and 'ありがとう (Arigatou)' can enhance your trip."
    elif destination == "New York":
        if month in [12, 1, 2]:
            weather = f"New York in {month_name} is cold (−2°C to 5°C) – heavy winter attire is a must."
        elif month in [3, 4, 5]:
            weather = f"In {month_name}, New York is mild (10-18°C) but can be unpredictable – dress in layers and bring a raincoat."
        elif month in [6, 7, 8]:
            weather = f"{month_name} in New York is hot and humid (25-30°C) – wear light clothing and stay hydrated."
        else:
            weather = f"During {month_name}, New York has moderate temperatures (10-20°C) – layered clothing is recommended."
        language = "English is the primary language."
    elif destination == "Goa":
        if month in [12, 1, 2]:
            weather = f"In {month_name}, Goa is cooler (20-25°C) and ideal for sightseeing – pack a light jacket for evenings."
        elif month in [3, 4, 5]:
            weather = f"{month_name} in Goa is warm (25-30°C) and dry – opt for very light, breathable clothing."
        elif month in [6, 7, 8]:
            weather = f"During {month_name}, Goa is hot and humid (28-33°C) with occasional rain – choose ultra-light clothes, use sunscreen, and stay hydrated."
        else:
            weather = f"In {month_name}, Goa is pleasantly warm (25-30°C) with a chance of brief showers – pack accordingly."
        language = "English is widely spoken along with Konkani. Basic English usually suffices."
    else:
        weather = f"Weather in {destination} during {month_name} can be variable – please check the forecast and pack accordingly."
        language = f"Local languages in {destination} may vary – consider learning a few basic phrases or using a translation app."
    return weather, language

def get_budget_tip(budget):
    """
    Returns a budget recommendation based on the user's input budget.
    """
    if budget < 30000:
        return "Opt for budget-friendly dining, public transport, and free attractions."
    elif budget < 70000:
        return "Mix economical choices with occasional splurges on well-reviewed experiences."
    else:
        return "Enjoy premium experiences, fine dining, and exclusive guided tours."

# ------------------ Preset Itinerary Data ------------------ #

preset_itineraries = {
    "Paris": [
        "Morning: Visit the Eiffel Tower and enjoy panoramic views.",
        "Late Morning: Explore the Louvre Museum to see timeless artworks.",
        "Afternoon: Savor lunch at a charming café along the Seine.",
        "Early Afternoon: Visit the exterior of Notre-Dame Cathedral and wander historic streets.",
        "Late Afternoon: Stroll through Montmartre and admire Sacré-Cœur Basilica.",
        "Evening: Dine in a traditional French bistro and sample local specialties.",
        "Night: Enjoy a scenic river cruise on the Seine with illuminated landmarks."
    ],
    "Tokyo": [
        "Morning: Begin at Senso-ji Temple in Asakusa and explore bustling market streets.",
        "Late Morning: Wander along Nakamise Street while sampling traditional snacks.",
        "Afternoon: Enjoy a sushi lunch at a renowned local eatery.",
        "Early Afternoon: Stroll through Ueno Park and visit eclectic museums.",
        "Late Afternoon: Experience the energy of Shibuya Crossing.",
        "Evening: Dine in Shinjuku and take in the lively nightlife.",
        "Night: Relax at an izakaya or enjoy city views from an observatory."
    ],
    "New York": [
        "Morning: Start with breakfast in Times Square to feel the city’s energy.",
        "Late Morning: Walk through Central Park, visiting iconic spots like Bethesda Terrace.",
        "Afternoon: Have lunch at a famous deli and visit a world-class museum.",
        "Early Afternoon: Explore trendy neighborhoods like SoHo for art and shopping.",
        "Late Afternoon: Take a ferry ride to see the Statue of Liberty up close.",
        "Evening: Enjoy a Broadway show followed by dinner at a top-tier restaurant.",
        "Night: Experience the vibrant nightlife or take a relaxing stroll through a buzzing district."
    ],
    "Goa": [
        "Morning: Relax on Baga Beach and watch a serene sunrise over the Arabian Sea.",
        "Late Morning: Explore Fort Aguada for its historic charm and coastal views.",
        "Afternoon: Savor a seafood lunch at a beachside shack.",
        "Early Afternoon: Tour a spice plantation to learn about local flavors.",
        "Late Afternoon: Enjoy water sports or take a boat ride along the coast.",
        "Evening: Stroll along the beach while sampling local street food.",
        "Night: Dine on authentic Goan cuisine and enjoy live music by the sea."
    ]
}

# ------------------ Streamlit App Layout ------------------ #

st.set_page_config(
    page_title="Travel Itinerary Planner",
    page_icon="🌍",
    layout="wide"
)

# Import Montserrat font from Google Fonts
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

css = """
<style>
body {
    background-color: #ADD8E6; /* Light blue background */
    font-family: 'Montserrat', sans-serif;
    color: #ffffff;
}
div[data-testid="stAppViewContainer"] {
    background: rgba(0, 0, 0, 0.8);
    padding: 20px;
    border-radius: 10px;
}
.sidebar-content {
    background: #011a33;
    border-radius: 10px;
    padding: 10px;
}
.itinerary-container {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    position: relative;
}
.itinerary-container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    border-radius: 10px;
    z-index: 1;
}
.itinerary-container * {
    position: relative;
    z-index: 2;
}
.day-header {
    font-size: 22px;
    font-weight: bold;
    color: #ffdc00; /* Gold for headers */
    margin-bottom: 5px;
}
.activities {
    font-size: 16px;
    color: #ffffff;
    margin: 3px 0;
}
.current-selections {
    color: #ffffff;
    background-color: rgba(0,0,0,0.7);
    padding: 10px;
    border-radius: 5px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ------------------ Sidebar: User Inputs ------------------ #

st.sidebar.header("Your Preferences")

dest_options = ["Paris", "Tokyo", "New York", "Goa", "Other"]
destination_choice = st.sidebar.selectbox("Select Your Destination", dest_options)
if destination_choice == "Other":
    destination = st.sidebar.text_input("Enter Your Destination", "")
else:
    destination = destination_choice

start_location = st.sidebar.text_input("Your Starting Location", "Enter your city")
budget = st.sidebar.slider("Your Budget (in INR)", 5000, 100000, 50000)
duration = st.sidebar.slider("Trip Duration (in days)", 1, 14, 5)
travel_date = st.sidebar.date_input("Select Your Travel Date", date.today())
travel_purpose = st.sidebar.multiselect(
    "Select Your Travel Purpose", 
    ["Vacation", "Business", "Family Trip", "Solo Travel", "Honeymoon", 
     "Adventure", "Cultural Exploration", "Wellness Retreat"]
)
preferences = st.sidebar.multiselect(
    "Choose Activities / Interests",
    ["Nature", "Culture", "Adventure", "Relaxation", "Historical Sites", 
     "Food & Cuisine", "Nightlife", "Shopping", "Arts & Entertainment", 
     "Local Experiences", "Offbeat Destinations"]
)

# ------------------ Display Current Selections ------------------ #

st.markdown("<div class='current-selections'>", unsafe_allow_html=True)
st.subheader("Your Current Selections")
st.markdown(f"**Destination:** {destination if destination else 'Not specified'}")
st.markdown(f"**Travel Date:** {travel_date}")
st.markdown(f"**Starting Location:** {start_location}")
st.markdown(f"**Budget (INR):** {budget}")
if travel_purpose:
    st.markdown("**Purpose(s):** " + ", ".join(travel_purpose))
if preferences:
    st.markdown("**Interest(s):** " + ", ".join(preferences))
st.markdown("</div>", unsafe_allow_html=True)

# ------------------ Generate Itinerary and Additional Advice ------------------ #

if st.button("Generate Itinerary"):
    
    if destination in preset_itineraries:
        base_points = preset_itineraries[destination]
        if destination == "Goa":
            extra_tasks = [
                "Explore local art galleries in Goa",
                "Attend a cultural performance in Goa",
                "Relax in one of Goa's scenic parks",
                "Visit an offbeat museum in Goa",
                "Experience the vibrant nightlife of Goa",
                "Take a local cooking class in Goa",
                "Shop at Mapusa Market in Goa",
                "Shop at Anjuna Flea Market in Goa",
                "Join a guided historical tour in Goa"
            ]
        elif destination == "Paris":
            extra_tasks = [
                "Explore chic boutiques and art galleries in Paris",
                "Attend a classical music concert in Paris",
                "Relax at a riverside park in Paris",
                "Visit a contemporary art museum in Paris",
                "Experience Parisian nightlife in trendy bars",
                "Take a pastry-making class in Paris",
                "Shop at local flea markets in Paris",
                "Join a guided walking tour in Montmartre"
            ]
        elif destination == "Tokyo":
            extra_tasks = [
                "Explore futuristic art galleries in Tokyo",
                "Attend a traditional Kabuki performance in Tokyo",
                "Relax in a serene Japanese garden in Tokyo",
                "Visit a modern museum in Tokyo",
                "Experience Tokyo's bustling nightlife in Shibuya",
                "Take a sushi-making class in Tokyo",
                "Shop at local district markets in Tokyo",
                "Join a guided tour of historical temples in Tokyo"
            ]
        elif destination == "New York":
            extra_tasks = [
                "Explore local art galleries in New York",
                "Attend a Broadway musical in New York",
                "Relax in Central Park",
                "Visit a cutting-edge museum in New York",
                "Experience New York's vibrant nightlife",
                "Take a culinary tour of New York's diverse neighborhoods",
                "Shop at trendy boutiques and street fairs in New York",
                "Join a guided historical tour of Manhattan"
            ]
        else:
            extra_tasks = [
                f"Explore local art galleries in {destination}",
                f"Attend a cultural performance in {destination}",
                f"Relax in a scenic park in {destination}",
                f"Visit a modern museum in {destination}",
                f"Experience vibrant nightlife in {destination}",
                f"Take a local cooking class in {destination}",
                f"Shop at local markets in {destination}",
                f"Join a guided historical tour in {destination}"
            ]
            
        global_tasks = list(set(base_points + extra_tasks))
        fallback_list = get_fallback_list(destination)
        global_pool = create_global_pool(global_tasks, fallback_list, destination, duration * 3)
        groups = generate_groups_from_global_pool(global_pool, duration, 3)
        itinerary = [{"Day": i + 1, "Activities": group} for i, group in enumerate(groups)]
    else:
        itinerary = fetch_itinerary_from_wiki(destination, duration)
        if not itinerary:
            st.warning("No live itinerary found. Using a generic itinerary based on your details.")
            fallback_list = get_fallback_list(destination)
            global_pool = create_global_pool([], fallback_list, destination, duration * 3)
            groups = generate_groups_from_global_pool(global_pool, duration, 3)
            itinerary = [{"Day": i + 1, "Activities": group} for i, group in enumerate(groups)]
    
    if start_location.strip() and start_location.lower() != destination.lower():
        departure_message = f"Take a flight from {start_location} to {destination}."
        itinerary[0]['Activities'] = [departure_message] + itinerary[0]['Activities']
        return_message = f"Take a flight from {destination} back to {start_location}."
        itinerary[-1]['Activities'].append(return_message)
    
    budget_tip = get_budget_tip(budget)
    for day in itinerary:
        day["Activities"].append(f"Budget Tip: {budget_tip}")
    
    st.subheader("Your Travel Itinerary")
    for day in itinerary:
        st.markdown("<div class='itinerary-container'>", unsafe_allow_html=True)
        st.markdown(f"<div class='day-header'>Day {day['Day']}</div>", unsafe_allow_html=True)
        for activity in day["Activities"]:
            st.markdown(f"<div class='activities'>• {activity}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    weather_info, language_info = get_travel_advice(destination, travel_date)
    st.subheader("Additional Travel Information")
    st.markdown(f"**Weather Advice:** {weather_info}")
    st.markdown(f"**Language Tips:** {language_info}")

# ------------------ Footer ------------------ #

st.markdown("---")
st.markdown(
    """
    <footer style="text-align: center; font-size: 12px;">
      Made with using Streamlit | © Ashutosh Garg
    </footer>
    """,
    unsafe_allow_html=True
)