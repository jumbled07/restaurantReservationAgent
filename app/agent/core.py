import json
import requests
from typing import Dict, List, Optional, Any
from .tools import ToolRegistry
from ..config import settings
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.conversation_history = []
        self.system_prompt = """You are a helpful restaurant reservation assistant. Your role is to help users:
1. Find and book restaurants
2. Manage their reservations
3. Get personalized recommendations
4. Handle special requests and dietary requirements

You have access to the following tools:
{tools}

When responding to users:
1. Be friendly and professional
2. Ask clarifying questions when needed
3. Provide specific details about restaurants
4. Handle errors gracefully
5. Confirm important details before making reservations
6. Suggest alternatives when appropriate

Format your responses in a clear, conversational manner."""

    def _get_tools_description(self) -> str:
        """Get a formatted description of available tools"""
        tools_desc = []
        for tool in self.tool_registry.tools.values():
            tools_desc.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tools_desc)

    def _create_prompt(self, user_message: str) -> str:
        """Create a prompt for the LLM including conversation history and available tools"""
        tools_desc = self._get_tools_description()
        system_prompt = self.system_prompt.format(tools=tools_desc)
        
        # Format conversation history
        conversation = []
        for msg in self.conversation_history[-5:]:  # Keep last 5 messages for context
            conversation.append(f"{msg['role']}: {msg['content']}")
        
        # Add current user message
        conversation.append(f"user: {user_message}")
        
        # Combine everything
        prompt = f"{system_prompt}\n\nConversation history:\n" + "\n".join(conversation)
        prompt += "\n\nassistant: Let me help you with that. "
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API to get a response"""
        try:
            # Check if API key is set
            logger.debug(f"Checking API key: {settings.LLM_API_KEY[:8]}..." if settings.LLM_API_KEY else "No API key set")
            if not settings.LLM_API_KEY:
                logger.error("No API key configured")
                return "I apologize, but I'm currently unable to process requests because the AI service is not properly configured. Please contact the system administrator to set up the required API key."
            
            headers = {
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            logger.debug(f"Making request to {settings.LLM_API_URL}")
            try:
                response = requests.post(
                    settings.LLM_API_URL,
                    headers=headers,
                    json=data,
                    timeout=10
                )
                logger.debug(f"Response status code: {response.status_code}")
                response.raise_for_status()
                
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                if e.response is not None:
                    logger.error(f"Response status: {e.response.status_code}")
                    logger.error(f"Response body: {e.response.text}")
                    if e.response.status_code == 401:
                        return "I apologize, but I'm currently unable to process requests because the AI service authentication failed. Please contact the system administrator to check the API key configuration."
                    elif e.response.status_code == 400:
                        return "I apologize, but I'm having trouble understanding the request format. Please try rephrasing your request."
                    else:
                        return f"I apologize, but I encountered an error while processing your request (Status: {e.response.status_code}). Please try again later."
                else:
                    return "I apologize, but I'm having trouble connecting to the AI service. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"I apologize, but I encountered an unexpected error: {str(e)}. Please try again later."

    def _extract_tool_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """Extract tool call information from LLM response"""
        try:
            # Look for tool call in the format: TOOL_CALL: {"tool": "tool_name", "parameters": {...}}
            if "TOOL_CALL:" in llm_response:
                tool_call_str = llm_response.split("TOOL_CALL:")[1].split("\n")[0].strip()
                return json.loads(tool_call_str)
            return None
        except Exception:
            return None

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        return self.tool_registry.execute_tool(tool_name, parameters)

    def _format_tool_response(self, tool_response: Dict[str, Any]) -> str:
        """Format tool response into a natural language response"""
        if tool_response["status"] == "error":
            return f"I apologize, but I encountered an error: {tool_response['message']}"
        
        data = tool_response.get("data", {})
        
        if "restaurants" in data:
            restaurants = data["restaurants"]
            if not restaurants:
                return "I couldn't find any restaurants matching your criteria. Would you like to try different search parameters?"
            
            response = "Here are some restaurants that match your criteria:\n\n"
            for r in restaurants[:3]:  # Show top 3 results
                response += f"- {r['name']} ({r['cuisine']}): {r['price_range']} in {r['location']}\n"
            if len(restaurants) > 3:
                response += f"\nAnd {len(restaurants) - 3} more options. Would you like to see more details about any of these restaurants?"
            return response
            
        elif "reservation" in data:
            reservation = data["reservation"]
            return f"Great! I've made your reservation at {reservation['restaurant_id']} for {reservation['date']} at {reservation['time']} for {reservation['party_size']} people. Your reservation ID is {data['reservation_id']}."
            
        elif "recommendations" in data:
            recommendations = data["recommendations"]
            if not recommendations:
                return "I couldn't find any recommendations based on your preferences. Would you like to try different criteria?"
            
            response = "Based on your preferences, here are some restaurants you might enjoy:\n\n"
            for r in recommendations[:3]:
                response += f"- {r['name']} ({r['cuisine']}): {r['price_range']} in {r['location']}\n"
            return response
            
        elif "reservations" in data:
            reservations = data["reservations"]
            if not reservations:
                return "You don't have any active reservations at the moment."
            
            response = "Here are your current reservations:\n\n"
            for r in reservations:
                restaurant = r["restaurant"]
                response += f"- {restaurant['name']} on {r['date']} at {r['time']} for {r['party_size']} people (Status: {r['status']})\n"
            return response
            
        elif "available" in data:
            if data["available"]:
                return f"Yes, there is availability for your requested time! The restaurant can accommodate your party of {data['available_capacity']} people."
            else:
                return f"I'm sorry, but the restaurant is fully booked for that time. They have {data['available_capacity']} seats available, but need {data['restaurant_capacity']} for your party. Would you like to try a different time?"
        
        return "I've processed your request successfully. Is there anything else you'd like to know?"

    def process_message(self, message: str, user_info: Optional[Dict[str, Any]] = None) -> str:
        """Process a user message and return a response"""
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Create prompt with conversation history
        prompt = self._create_prompt(message)
        
        # Get LLM response
        llm_response = self._call_llm(prompt)
        
        # Check for tool call
        tool_call = self._extract_tool_call(llm_response)
        if tool_call:
            # Execute tool
            tool_response = self._execute_tool(
                tool_call["tool"],
                {**tool_call["parameters"], "user_info": user_info}
            )
            
            # Format tool response
            response = self._format_tool_response(tool_response)
        else:
            # Use LLM response directly
            response = llm_response
        
        # Add assistant response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response 