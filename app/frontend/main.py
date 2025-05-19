import streamlit as st
import requests
from typing import Dict, Any, Optional, List
import json
from datetime import datetime, timedelta

# Initialize session state variables
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'explore'
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = None
if 'availability_confirmed' not in st.session_state:
    st.session_state.availability_confirmed = False
if 'viewing_menu' not in st.session_state:
    st.session_state.viewing_menu = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = True
if 'show_quick_book' not in st.session_state:
    st.session_state.show_quick_book = False

def check_backend_health() -> bool:
    """Check if backend server is healthy"""
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_restaurants(filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Get list of restaurants with optional filters"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/restaurants",
            params=filters,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching restaurants: {str(e)}")
        return []

def check_restaurant_availability(restaurant_name: str, date: str, time: str, party_size: int) -> Dict[str, Any]:
    """Check restaurant availability"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": f"Check availability for {restaurant_name} on {date} at {time} for {party_size} people",
                "user_info": st.session_state.user_info
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error checking availability: {str(e)}")
        return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email if they exist"""
    try:
        response = requests.get(f"http://localhost:8000/api/v1/users/email/{email}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create or look up a user in the backend"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/users",
            json=user_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error creating user profile: {str(e)}")
        return None

def display_restaurant_card(restaurant: Dict[str, Any]):
    """Display a restaurant card with key information"""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(restaurant["name"])
        st.write(f"📍 {restaurant['location']}")
        st.write(f"🍽️ {restaurant['cuisine']}")
        st.write(f"💰 {restaurant['price_range']}")
        st.write(f"⭐ {restaurant['rating']}/5")
    with col2:
        if st.button("View Menu", key=f"menu_{restaurant['id']}"):
            st.session_state.viewing_menu = True
            st.session_state.selected_restaurant = restaurant
            st.session_state.current_step = 'view_menu'
            st.experimental_rerun()
        if st.button("Book Now", key=f"book_{restaurant['id']}"):
            st.session_state.selected_restaurant = restaurant
            st.session_state.current_step = 'user_info'
            st.experimental_rerun()
    st.divider()

def display_menu(restaurant: Dict[str, Any]):
    """Display restaurant menu"""
    st.header(f"{restaurant['name']} - Menu")
    
    # Display menu categories
    for category, items in restaurant['menu'].items():
        st.subheader(category)
        for item in items:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{item['name']}**")
                if 'description' in item:
                    st.write(item['description'])
            with col2:
                st.write(f"${item['price']:.2f}")
        st.divider()
    
    if st.button("Back to Restaurants"):
        st.session_state.viewing_menu = False
        st.session_state.current_step = 'explore'
        st.experimental_rerun()

def get_recommendations() -> Dict[str, Any]:
    """Get restaurant recommendations"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": "What are some good restaurant recommendations or special deals today?",
                "user_info": st.session_state.user_info
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return None

WELCOME_MESSAGE = {
    "role": "assistant",
    "content": """👋 Welcome to the Restaurant Assistant! I can help you:

• Find restaurants by cuisine, location, or price range
• Get personalized recommendations
• View menus and make reservations
• Check for special deals and events

What would you like to do today? You can:
- Ask for recommendations (e.g., "What are some good Italian restaurants?")
- Search by cuisine (e.g., "Show me Mexican restaurants")
- Check for deals (e.g., "Any special offers today?")
- Make a reservation (e.g., "I want to book a table at [restaurant name]")

Feel free to ask anything!"""
}

def display_suggested_queries():
    suggested_queries = [
        "Show me Italian restaurants",
        "Any deals today?",
        "Book a table at La Bella Italia",
        "Find vegetarian options",
        "Show top rated restaurants"
    ]
    st.markdown("**Quick Suggestions:**")
    cols = st.columns(len(suggested_queries))
    for i, query in enumerate(suggested_queries):
        if cols[i].button(query, key=f"suggestion_{i}"):
            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })
            st.session_state.chat_input_value = ""
            st.session_state.suggestion_clicked = False
            st.rerun()

def display_quick_book_form():
    st.header("Quick Book a Restaurant")
    restaurants = get_restaurants()
    restaurant_names = [r["name"] for r in restaurants]
    selected_name = st.selectbox("Select Restaurant", restaurant_names)
    restaurant = next((r for r in restaurants if r["name"] == selected_name), None)
    if not restaurant:
        st.warning("Please select a restaurant.")
        return
    with st.form("quick_book_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        date = st.date_input("Date")
        time = st.time_input("Time")
        party_size = st.number_input("Party Size", min_value=1, max_value=restaurant.get('capacity', 20), value=2)
        special_requests = st.text_area("Special Requests or Dietary Requirements")
        submitted = st.form_submit_button("Book Reservation")
        if submitted:
            if not all([name, email, phone, date, time, party_size]):
                st.error("Please fill in all required fields")
            else:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "preferences": {},
                    "special_requests": special_requests
                }
                user = create_user(user_data)
                if user and user.get("id"):
                    reservation_data = {
                        "restaurant_id": restaurant["id"],
                        "user_id": user["id"],
                        "date": str(date),
                        "time": str(time),
                        "party_size": party_size,
                        "special_requests": special_requests
                    }
                    result = make_reservation(reservation_data)
                    if result:
                        st.success("Your reservation has been made!")
                        st.session_state.current_step = "explore"
                        st.session_state.selected_restaurant = None
                        st.rerun()

def display_chat_interface():
    st.subheader("Restaurant Assistant")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            # Show Book Now button for mentioned restaurant
            if message.get("mentioned_restaurant"):
                restaurant = message["mentioned_restaurant"]
                if st.button(f"Book Now at {restaurant['name']}", key=f"book_mentioned_{restaurant['name']}"):
                    st.session_state.selected_restaurant = restaurant
                    st.session_state.current_step = "reservation_form"
                    st.rerun()
            # Show Book Now buttons for recommended restaurants
            if message.get("recommended_restaurants"):
                for restaurant in message["recommended_restaurants"]:
                    if st.button(f"Book Now at {restaurant['name']}", key=f"book_rec_{restaurant['name']}"):
                        st.session_state.selected_restaurant = restaurant
                        st.session_state.current_step = "reservation_form"
                        st.rerun()
        # Show suggested queries after each assistant message
        if message["role"] == "assistant":
            display_suggested_queries()

def process_chat_message(message: str) -> Dict[str, Any]:
    """Process a chat message and get response"""
    try:
        # Check if the user mentions a specific restaurant
        restaurants = get_restaurants()
        mentioned_restaurant = None
        for restaurant in restaurants:
            if restaurant["name"].lower() in message.lower():
                mentioned_restaurant = restaurant
                break
        if mentioned_restaurant:
            return {
                "response": f"Would you like to book a table at {mentioned_restaurant['name']}?",
                "mentioned_restaurant": mentioned_restaurant
            }
        # Otherwise, get recommendations from backend
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": message,
                "user_info": st.session_state.get("user_info", None)
            },
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        # Try to extract recommended restaurants from the response
        recommended_restaurants = []
        if result and result.get("response"):
            for restaurant in restaurants:
                if restaurant["name"].lower() in result["response"].lower():
                    recommended_restaurants.append(restaurant)
        if recommended_restaurants:
            return {
                "response": result["response"],
                "recommended_restaurants": recommended_restaurants
            }
        return result
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        return None

def display_back_button():
    """Display back button based on current step"""
    if st.session_state.current_step != 'explore':
        if st.button("← Back"):
            if st.session_state.current_step == 'view_menu':
                st.session_state.viewing_menu = False
                st.session_state.current_step = 'explore'
            elif st.session_state.current_step == 'availability':
                st.session_state.current_step = 'explore'
            elif st.session_state.current_step == 'user_info':
                st.session_state.current_step = 'availability'
            elif st.session_state.current_step == 'confirm_reservation':
                st.session_state.current_step = 'user_info'
            st.experimental_rerun()

def make_reservation(reservation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create a reservation in the backend"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/reservations",
            json=reservation_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error making reservation: {str(e)}")
        return None

def display_confirm_reservation():
    st.header("Confirm Your Reservation")
    restaurant = st.session_state.selected_restaurant
    user = st.session_state.user_info
    st.subheader("Reservation Details")
    st.write(f"Restaurant: {restaurant['name']}")
    st.write(f"Location: {restaurant['location']}")
    st.write(f"Cuisine: {restaurant['cuisine']}")
    st.write(f"Price Range: {restaurant['price_range']}")
    st.write(f"Party Size: {restaurant.get('party_size', 2)}")
    st.write(f"Date: {restaurant.get('date', 'Not set')}")
    st.write(f"Time: {restaurant.get('time', 'Not set')}")
    st.subheader("Your Information")
    st.write(f"Name: {user['name']}")
    st.write(f"Email: {user['email']}")
    st.write(f"Phone: {user['phone']}")
    st.write(f"Preferences: {user.get('preferences', {})}")
    st.write(f"Special Requests: {user.get('special_requests', '')}")
    if st.button("Confirm Reservation"):
        reservation_data = {
            "restaurant_id": restaurant["id"],
            "user_id": user["id"],
            "date": restaurant.get("date", ""),
            "time": restaurant.get("time", ""),
            "party_size": restaurant.get("party_size", 2),
            "special_requests": user.get("special_requests", "")
        }
        result = make_reservation(reservation_data)
        if result:
            st.success("Your reservation has been made!")
            st.session_state.current_step = "explore"
            st.session_state.selected_restaurant = None
            st.session_state.user_info = None
            st.rerun()
    if st.button("Cancel Reservation"):
        st.session_state.current_step = "explore"
        st.session_state.selected_restaurant = None
        st.session_state.user_info = None
        st.rerun()

def display_user_info_form():
    st.header("Complete Your Reservation")
    with st.form("user_info_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        cuisine_types = st.multiselect(
            "Preferred Cuisine Types",
            ["Italian", "Japanese", "Indian", "Mexican", "American", "Chinese", "Thai", "French"]
        )
        price_range = st.select_slider(
            "Preferred Price Range",
            options=["$", "$$", "$$$", "$$$$"],
            value="$$"
        )
        location = st.text_input("Preferred Location")
        special_requests = st.text_area("Special Requests or Dietary Requirements")
        submitted = st.form_submit_button("Submit Reservation Details")
        if submitted:
            if not all([name, email, phone]):
                st.error("Please fill in all required fields")
            else:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "preferences": {
                        "cuisine_types": cuisine_types,
                        "price_range": price_range,
                        "location": location
                    },
                    "special_requests": special_requests
                }
                user = create_user(user_data)
                if user:
                    st.session_state.user_info = user
                    st.session_state.current_step = "confirm_reservation"
                    st.experimental_rerun()

def display_reservation_form():
    st.header("Book Your Reservation")
    restaurant = st.session_state.selected_restaurant
    st.subheader(f"Restaurant: {restaurant['name']}")
    with st.form("reservation_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        cuisine_types = st.multiselect(
            "Preferred Cuisine Types",
            ["Italian", "Japanese", "Indian", "Mexican", "American", "Chinese", "Thai", "French"]
        )
        price_range = st.select_slider(
            "Preferred Price Range",
            options=["$", "$$", "$$$", "$$$$"],
            value="$$"
        )
        location = st.text_input("Preferred Location")
        date = st.date_input("Date")
        time = st.time_input("Time")
        party_size = st.number_input("Party Size", min_value=1, max_value=restaurant.get('capacity', 20), value=2)
        special_requests = st.text_area("Special Requests or Dietary Requirements")
        submitted = st.form_submit_button("Book Reservation")
        if submitted:
            if not all([name, email, phone, date, time, party_size]):
                st.error("Please fill in all required fields")
            else:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "preferences": {
                        "cuisine_types": cuisine_types,
                        "price_range": price_range,
                        "location": location
                    },
                    "special_requests": special_requests
                }
                user = create_user(user_data)
                if user and user.get("id"):
                    reservation_data = {
                        "restaurant_id": restaurant["id"],
                        "user_id": user["id"],
                        "date": str(date),
                        "time": str(time),
                        "party_size": party_size,
                        "special_requests": special_requests
                    }
                    result = make_reservation(reservation_data)
                    if result:
                        st.success("Your reservation has been made!")
                        st.session_state.current_step = "explore"
                        st.session_state.selected_restaurant = None
                        st.rerun()

def main():
    st.set_page_config(
        page_title="Restaurant Reservation System",
        page_icon="🍽️",
        layout="wide"
    )
    st.title("Restaurant Reservation System")
    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.session_state.chat_history = [WELCOME_MESSAGE]
    if "current_step" not in st.session_state:
        st.session_state.current_step = "explore"
    if "selected_restaurant" not in st.session_state:
        st.session_state.selected_restaurant = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "viewing_menu" not in st.session_state:
        st.session_state.viewing_menu = False
    if "show_quick_book" not in st.session_state:
        st.session_state.show_quick_book = False
    display_chat_interface()
    # Quick Book button at the top
    if st.button("Quick Book a Restaurant", key="quick_book_top"):
        st.session_state.show_quick_book = True
        st.session_state.current_step = "quick_book_form"
        st.experimental_rerun()
    if st.session_state.current_step == 'quick_book_form':
        display_quick_book_form()
        return
    # Explore Restaurants section
    if st.session_state.current_step == 'explore':
        st.header("Explore Restaurants")
        col1, col2, col3 = st.columns(3)
        with col1:
            cuisine = st.selectbox(
                "Cuisine Type",
                ["All", "Italian", "Japanese", "Indian", "Mexican", "American", "Chinese", "Thai", "French"]
            )
        with col2:
            price_range = st.selectbox(
                "Price Range",
                ["All", "$", "$$", "$$$", "$$$$"]
            )
        with col3:
            location = st.text_input("Location")
        filters = {}
        if cuisine != "All":
            filters["cuisine"] = cuisine
        if price_range != "All":
            filters["price_range"] = price_range
        if location:
            filters["location"] = location
        restaurants = get_restaurants(filters)
        if not restaurants:
            st.info("No restaurants found matching your criteria. Try adjusting the filters.")
        else:
            for restaurant in restaurants:
                display_restaurant_card(restaurant)
    # View Menu
    elif st.session_state.current_step == 'view_menu':
        display_menu(st.session_state.selected_restaurant)
    # User Info Form
    elif st.session_state.current_step == "user_info":
        display_user_info_form()
        return
    # Confirm Reservation
    elif st.session_state.current_step == "confirm_reservation":
        display_confirm_reservation()
        return
    # Reservation Form
    elif st.session_state.current_step == "reservation_form":
        display_reservation_form()
        return
    # Chat input
    prompt = st.chat_input("Ask about restaurants, deals, or recommendations...")
    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_chat_message(prompt)
                if response:
                    chat_response = {
                        "role": "assistant",
                        "content": response.get("response", "")
                    }
                    if "mentioned_restaurant" in response:
                        chat_response["mentioned_restaurant"] = response["mentioned_restaurant"]
                    if "recommended_restaurants" in response:
                        chat_response["recommended_restaurants"] = response["recommended_restaurants"]
                    st.session_state.chat_history.append(chat_response)
                    st.rerun()

if __name__ == "__main__":
    main() 