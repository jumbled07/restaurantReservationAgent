# Restaurant Reservation Agent

An intelligent restaurant reservation system powered by AI that provides personalized restaurant recommendations, handles reservations, and offers a concierge-like experience through natural conversation.

## 🚀 Features

- **AI-Powered Chat Interface**: Natural language interaction for restaurant discovery and booking
- **Smart Recommendations**: Personalized restaurant suggestions based on user preferences
- **Streamlined Booking**: Quick booking process with availability checking
- **User Management**: Seamless handling of new and returning customers
- **Restaurant Exploration**: Browse restaurants by cuisine, price range, and location
- **Menu Viewing**: Detailed restaurant menus with prices and descriptions

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Groq API key (for AI capabilities)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/restaurantReservationAgent.git
cd restaurantReservationAgent
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

5. Start the backend server:
```bash
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

6. In a new terminal, start the frontend:
```bash
streamlit run app/frontend/main.py
```

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000

## 🤖 Prompt Engineering Approach

### System Prompt Design
The AI agent is designed with a concierge-like personality, focusing on:
1. **Contextual Understanding**: Maintains conversation history and user preferences
2. **Natural Interaction**: Uses friendly, professional language
3. **Proactive Assistance**: Offers relevant suggestions and alternatives
4. **Error Handling**: Gracefully manages misunderstandings and limitations

### Key Prompt Components
```python
system_prompt = """You are a helpful restaurant reservation assistant. Your role is to help users:
1. Find and book restaurants
2. Manage their reservations
3. Get personalized recommendations
4. Handle special requests and dietary requirements

When responding to users:
1. Be friendly and professional
2. Ask clarifying questions when needed
3. Provide specific details about restaurants
4. Handle errors gracefully
5. Confirm important details before making reservations
6. Suggest alternatives when appropriate"""
```

### Tool Integration
The agent uses a tool-based approach to:
1. Check restaurant availability
2. Make reservations
3. Get restaurant recommendations
4. Manage user preferences
5. Handle special requests

## 💬 Example Conversations

### 1. New User - Restaurant Discovery
```
User: Hi, I'm looking for a nice Italian restaurant for a date night
Assistant: I'd be happy to help you find the perfect Italian restaurant for your date night! I can see a few great options:

- The Italian Bistro: Romantic atmosphere, candlelit tables (Italian, $$, Downtown)
- Bella Italia: Authentic cuisine, live music on weekends (Italian, $$$, Westside)
- Pasta Paradise: Cozy setting, extensive wine list (Italian, $$, Eastside)

Would you like to know more about any of these restaurants? I can tell you about their special dishes, ambiance, or help you check availability for your preferred date and time.

User: Tell me more about The Italian Bistro
Assistant: The Italian Bistro is a charming restaurant known for its romantic atmosphere and authentic Italian cuisine. They offer:
- Candlelit tables and intimate seating
- A special date night menu available Tuesday through Thursday
- Live piano music on weekends
- Extensive wine selection with sommelier service
- Signature dishes include their homemade pasta and tiramisu

Would you like to check their availability for a specific date? I can help you make a reservation right away!
```

### 2. Returning User - Quick Booking
```
User: I want to book a table for 4 at Sushi Master tomorrow at 7 PM
Assistant: I'll help you check availability at Sushi Master for tomorrow at 7 PM for 4 people.

[Checking availability...]

Great news! They have a table available for 4 people tomorrow at 7 PM. I see you've dined with us before. Would you like me to proceed with the booking using your existing account?

User: Yes, please
Assistant: Perfect! I've made your reservation at Sushi Master for tomorrow at 7 PM for 4 people. Your reservation ID is #12345. You'll receive a confirmation email shortly.

Is there anything else you'd like to know about your reservation? I can help with:
- Special dietary requirements
- Parking information
- Menu preview
- Cancellation policy
```

### 3. Special Requests
```
User: I need a restaurant that can accommodate my gluten-free diet
Assistant: I'll help you find restaurants that can accommodate your gluten-free requirements. Here are some excellent options:

- Green Garden: Dedicated gluten-free menu, certified kitchen (American, $$, Downtown)
- Spice Garden: Extensive gluten-free Indian options (Indian, $$, Eastside)
- The Healthy Plate: Specializes in dietary restrictions (International, $$, Westside)

All these restaurants have trained staff who understand gluten-free requirements and can ensure safe preparation of your meal. Would you like to know more about any of these options or shall I help you make a reservation?

User: Tell me about Green Garden's gluten-free options
Assistant: Green Garden is known for their exceptional handling of dietary restrictions. Their gluten-free offerings include:

- Dedicated gluten-free kitchen area
- Separate preparation utensils and equipment
- Certified gluten-free menu items
- Knowledgeable staff trained in food allergies
- Popular gluten-free dishes:
  * Quinoa Buddha Bowl
  * Grilled Salmon with seasonal vegetables
  * Gluten-free pasta options
  * Flourless chocolate cake

Would you like to see their full menu or check availability for a specific date?
```

## 📈 Business Strategy

### Target Market
1. **Primary Users**:
   - Busy professionals seeking convenient booking
   - Food enthusiasts looking for new experiences
   - Special occasion planners
   - Dietary restriction-conscious diners

2. **Restaurant Partners**:
   - High-quality establishments
   - Restaurants with unique offerings
   - Venues with good availability management
   - Establishments with strong customer service

### Value Proposition
1. **For Users**:
   - Time-saving booking process
   - Personalized recommendations
   - Special request handling
   - Seamless user experience

2. **For Restaurants**:
   - Increased visibility
   - Better table management
   - Customer preference insights
   - Reduced no-shows

### Growth Strategy
1. **Short-term**:
   - Expand restaurant network
   - Enhance AI capabilities
   - Implement user feedback system
   - Add more personalization features

2. **Long-term**:
   - Mobile app development
   - Integration with restaurant POS systems
   - Loyalty program implementation
   - Expansion to new markets

### Competitive Advantage
1. **AI-Powered Personalization**: Better recommendations than traditional booking systems
2. **Natural Language Interface**: More intuitive than form-based booking
3. **Comprehensive Service**: Handles everything from discovery to booking
4. **User-Centric Design**: Focuses on customer experience and convenience

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.