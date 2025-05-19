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
    """Create a new user"""
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
            st.session_state.current_step = 'availability'
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

def process_chat_message(message: str) -> Dict[str, Any]:
    """Process a chat message and get response"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "message": message,
                "user_info": st.session_state.user_info
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        return None

def display_chat_interface():
    """Display chat interface with recommendations and booking options"""
    st.subheader("Restaurant Assistant")
    
    # Display chat history using Streamlit's chat components
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Parse the message for restaurant suggestions
                if "Here are some restaurants" in message["content"] or "Based on your preferences" in message["content"]:
                    # Split the message into lines
                    lines = message["content"].split("\n")
                    for line in lines:
                        if line.startswith("- "):  # This is a restaurant suggestion
                            # Extract restaurant name and details
                            parts = line[2:].split(" (")
                            if len(parts) >= 1:
                                restaurant_name = parts[0]
                                details = parts[1].rstrip(")") if len(parts) > 1 else ""
                                
                                # Create columns for the restaurant info and button
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**{restaurant_name}** ({details})")
                                with col2:
                                    if st.button("Book Now", key=f"book_{restaurant_name}"):
                                        # Set the restaurant name in the search
                                        st.session_state.restaurant_name = restaurant_name
                                        # Move to availability check step
                                        st.session_state.current_step = "check_availability"
                                        st.rerun()
                        else:
                            st.write(line)
                else:
                    st.write(message["content"])
            else:
                st.write(message["content"])
    
    # Show recommendations if enabled
    if st.session_state.show_recommendations:
        with st.chat_message("assistant"):
            with st.spinner("Getting recommendations..."):
                recommendations = get_recommendations()
                if recommendations and recommendations.get("response"):
                    st.write(recommendations["response"])
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": recommendations["response"]
                    })
                    st.session_state.show_recommendations = False
    
    # Chat input using Streamlit's chat input
    if prompt := st.chat_input("Ask about restaurants, deals, or recommendations..."):
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_chat_message(prompt)
                if response and response.get("response"):
                    st.write(response["response"])
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["response"]
                    })
                    
                    # If the response suggests getting user preferences
                    if "preferences" in response["response"].lower() and not st.session_state.user_info:
                        st.info("Would you like to save your preferences for better recommendations?")
                        if st.button("Save Preferences"):
                            st.session_state.current_step = 'user_info'
                            st.experimental_rerun()

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

def main():
    # Set page config with custom favicon
    st.set_page_config(
        page_title="Restaurant Reservation System",
        page_icon="🍽️",  # Using a plate with fork and knife emoji as favicon
        layout="wide"
    )
    
    st.title("Restaurant Reservation System")
    
    # Initialize session state variables if they don't exist
    if "current_step" not in st.session_state:
        st.session_state.current_step = "explore"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add initial recommendations
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": """Welcome! I can help you find and book restaurants. Here are some current special deals:

- The Italian Bistro: 20% off on weekdays (Italian, $$, Downtown)
- Sushi Master: Happy Hour 5-7 PM (Japanese, $$$, Westside)
- Spice Garden: Family Dinner Special (Indian, $$, Eastside)

Would you like to know more about any of these restaurants or would you prefer different recommendations?"""
        })
    if "restaurant_name" not in st.session_state:
        st.session_state.restaurant_name = ""
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "show_recommendations" not in st.session_state:
        st.session_state.show_recommendations = True
    if "selected_restaurant" not in st.session_state:
        st.session_state.selected_restaurant = None
    if "viewing_menu" not in st.session_state:
        st.session_state.viewing_menu = False
    if "reservation_date" not in st.session_state:
        st.session_state.reservation_date = None
    if "reservation_time" not in st.session_state:
        st.session_state.reservation_time = None
    if "party_size" not in st.session_state:
        st.session_state.party_size = None
    if "availability_checked" not in st.session_state:
        st.session_state.availability_checked = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "existing_user" not in st.session_state:
        st.session_state.existing_user = None
    if "reservation_confirmed" not in st.session_state:
        st.session_state.reservation_confirmed = False

    # Check backend health
    if not check_backend_health():
        st.error("Backend server is not available. Please ensure the server is running.")
        return

    # Display chat interface at the top
    display_chat_interface()
    
    # Display back button
    display_back_button()
    
    st.divider()

    # Step 1: Restaurant Exploration
    if st.session_state.current_step == 'explore':
        st.header("Explore Restaurants")
        
        # Filters
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
        
        # Apply filters
        filters = {}
        if cuisine != "All":
            filters["cuisine"] = cuisine
        if price_range != "All":
            filters["price_range"] = price_range
        if location:
            filters["location"] = location
        
        # Get and display restaurants
        restaurants = get_restaurants(filters)
        if not restaurants:
            st.info("No restaurants found matching your criteria. Try adjusting the filters.")
        else:
            for restaurant in restaurants:
                display_restaurant_card(restaurant)

    # Step 2: View Menu
    elif st.session_state.current_step == 'view_menu':
        display_menu(st.session_state.selected_restaurant)

    # Step 3: Restaurant Availability Check
    elif st.session_state.current_step == 'availability':
        st.header("Check Availability")
        
        # Show restaurant details
        st.subheader("Restaurant Details")
        restaurant = st.session_state.selected_restaurant
        st.write(f"Name: {restaurant['name']}")
        st.write(f"Cuisine: {restaurant['cuisine']}")
        st.write(f"Location: {restaurant['location']}")
        
        # Availability form
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", min_value=datetime.now().date())
            time = st.time_input("Time")
        with col2:
            party_size = st.number_input("Party Size", min_value=1, max_value=restaurant['capacity'], value=2)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check Availability"):
                with st.spinner("Checking availability..."):
                    date_str = date.strftime("%Y-%m-%d")
                    time_str = time.strftime("%H:%M")
                    response = check_restaurant_availability(
                        restaurant['name'], date_str, time_str, party_size
                    )
                    
                    if response and response.get("response"):
                        st.session_state.selected_restaurant.update({
                            "date": date_str,
                            "time": time_str,
                            "party_size": party_size
                        })
                        st.session_state.availability_confirmed = True
                        st.success(response["response"])
                        st.session_state.current_step = 'user_info'
                        st.experimental_rerun()

    # Step 4: User Information (only if availability is confirmed)
    elif st.session_state.current_step == 'user_info' and st.session_state.availability_confirmed:
        st.header("Complete Your Reservation")
        
        # Show reservation details
        st.subheader("Reservation Details")
        restaurant = st.session_state.selected_restaurant
        st.write(f"Restaurant: {restaurant['name']}")
        st.write(f"Date: {restaurant['date']}")
        st.write(f"Time: {restaurant['time']}")
        st.write(f"Party Size: {restaurant['party_size']}")
        
        # If user is not logged in, show login/registration form
        if not st.session_state.user_info:
            st.subheader("Please provide your information")
            
            # First try to get user by email
            email = st.text_input("Email")
            if email and st.button("Check Existing Account"):
                user = get_user_by_email(email)
                if user:
                    st.session_state.user_info = user
                    st.success("Welcome back! Your account has been found.")
                    st.session_state.current_step = 'confirm_reservation'
                    st.experimental_rerun()
                else:
                    st.info("No existing account found. Please complete the registration form.")
            
            # Registration form
            with st.form("user_info_form"):
                name = st.text_input("Full Name")
                phone = st.text_input("Phone Number")
                
                st.subheader("Preferences")
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
                
                submitted = st.form_submit_button("Complete Registration")
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
                            st.success("Account created successfully!")
                            st.session_state.current_step = 'confirm_reservation'
                            st.experimental_rerun()

    # Step 5: Confirm Reservation
    elif st.session_state.current_step == 'confirm_reservation':
        st.header("Confirm Your Reservation")
        
        # Show all details
        st.subheader("Reservation Details")
        restaurant = st.session_state.selected_restaurant
        st.write(f"Restaurant: {restaurant['name']}")
        st.write(f"Date: {restaurant['date']}")
        st.write(f"Time: {restaurant['time']}")
        st.write(f"Party Size: {restaurant['party_size']}")
        
        st.subheader("Your Information")
        st.write(f"Name: {st.session_state.user_info['name']}")
        st.write(f"Email: {st.session_state.user_info['email']}")
        st.write(f"Phone: {st.session_state.user_info['phone']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Reservation"):
                with st.spinner("Processing your reservation..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/v1/chat",
                            json={
                                "message": f"Make reservation at {restaurant['name']} on {restaurant['date']} at {restaurant['time']} for {restaurant['party_size']} people",
                                "user_info": st.session_state.user_info
                            },
                            timeout=10
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        if result and result.get("response"):
                            st.success(result["response"])
                            # Reset the flow
                            st.session_state.current_step = 'explore'
                            st.session_state.selected_restaurant = None
                            st.session_state.availability_confirmed = False
                            st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error making reservation: {str(e)}")
        with col2:
            if st.button("Cancel Reservation"):
                st.session_state.current_step = 'explore'
                st.session_state.selected_restaurant = None
                st.session_state.availability_confirmed = False
                st.experimental_rerun()

if __name__ == "__main__":
    main() 