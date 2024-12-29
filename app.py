import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from typing import Dict, List

class RecyclingEcommerceChatbot:
    def __init__(self, api_key: str):
        """
        Initialize the chatbot with Gemini API integration

        :param api_key: Google Gemini API key
        """
        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # Set up the model
        self.model = genai.GenerativeModel('gemini-pro')

        # Predefined context for recycling and sustainability
        self.context = """
        You are an AI assistant for an eco-friendly e-commerce platform 
        focused on recycling and sustainable products. 
        Your goals are to:
        1. Help users find sustainable products
        2. Provide recycling advice
        3. Explain environmental impact of purchases
        4. Suggest eco-friendly alternatives
         """

    def generate_product_recommendations(self, user_preferences: Dict) -> List[Dict]:
        """
        Generate personalized product recommendations

        :param user_preferences: User's preferences and interests
        :return: List of recommended products
        """
        prompt = f"""
        Based on these user preferences: {user_preferences}
        Recommend 3-5 sustainable products from our eco-friendly collection.
        For each product, provide:
        - Product name
        - Brief description
        - Environmental impact reduction
        - Price range
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_product_recommendations(response.text)
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

    def _parse_product_recommendations(self, response_text: str) -> List[Dict]:
        """
        Parse the text response into structured product recommendations

        :param response_text: Raw text from Gemini API
        :return: Parsed product recommendations
        """
        # Simple parsing logic (you'd want to improve this)
        recommendations = []
        lines = response_text.split('\n')
        current_product = {}

        for line in lines:
            if line.startswith('- Product name:'):
                if current_product:
                    recommendations.append(current_product)
                current_product = {'name': line.split(':')[1].strip()}
            elif line.startswith('- Brief description:'):
                current_product['description'] = line.split(':')[1].strip()
            elif line.startswith('- Environmental impact reduction:'):
                current_product['impact_reduction'] = line.split(':')[1].strip()
            elif line.startswith('- Price range:'):
                current_product['price_range'] = line.split(':')[1].strip()

        if current_product:
            recommendations.append(current_product)

        return recommendations

    def chat_response(self, user_message: str) -> str:
        """
        Generate a conversational response

        :param user_message: User's input message
        :return: AI-generated response
        """
        try:
            full_prompt = f"{self.context}\n\nUser Message: {user_message}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error in chat response: {e}")
            return "I'm having trouble processing your message. Could you please try again?"


# Flask Application Setup
app = Flask(__name__)

# Initialize the chatbot (replace with your actual API key)
GEMINI_API_KEY = "ُEnter your api key"
chatbot = RecyclingEcommerceChatbot(GEMINI_API_KEY)


# Routes
@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Generate product recommendations based on user preferences
    """
    try:
        preferences = request.json
        recommendations = chatbot.generate_product_recommendations(preferences)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat interactions
    """
    try:
        user_message = request.json.get('message', '')
        response = chatbot.chat_response(user_message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error ': str(e)}), 500


if __name__ == '__main__':
    # save_project_files()
    app.run(debug=True) 
