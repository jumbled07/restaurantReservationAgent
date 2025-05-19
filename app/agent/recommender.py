from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from ..storage.file_storage import FileStorage

class RestaurantRecommender:
    def __init__(self):
        self.storage = FileStorage()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._update_vectors()

    def _update_vectors(self):
        """Update restaurant vectors when data changes"""
        restaurants = self.storage.get_restaurants()
        if not restaurants:
            self.restaurant_vectors = None
            self.restaurant_ids = []
            return

        # Create text features for each restaurant
        restaurant_texts = []
        self.restaurant_ids = []
        for r in restaurants:
            features = [
                r['name'],
                r['cuisine'],
                r['location'],
                r['price_range'],
                ' '.join(str(v) for v in r['features'].values()),
                ' '.join(item['name'] for category in r['menu'].values() for item in category)
            ]
            restaurant_texts.append(' '.join(features))
            self.restaurant_ids.append(r['id'])

        # Create TF-IDF vectors
        self.restaurant_vectors = self.vectorizer.fit_transform(restaurant_texts)

    def _get_user_preferences_vector(self, user_preferences: Dict) -> np.ndarray:
        """Convert user preferences to a vector"""
        if not user_preferences:
            return None

        preferences_text = ' '.join([
            user_preferences.get('cuisine_preference', ''),
            user_preferences.get('location', ''),
            user_preferences.get('price_range', ''),
            ' '.join(user_preferences.get('dietary_restrictions', [])),
            user_preferences.get('occasion', '')
        ])
        
        return self.vectorizer.transform([preferences_text])

    def get_recommendations(
        self,
        user_id: Optional[int] = None,
        cuisine_preference: Optional[str] = None,
        location: Optional[str] = None,
        price_range: Optional[str] = None,
        occasion: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Get restaurant recommendations based on preferences"""
        if not self.restaurant_vectors or not self.restaurant_ids:
            self._update_vectors()
            if not self.restaurant_vectors:
                return []

        # Get user preferences if user_id is provided
        user_preferences = {}
        if user_id:
            user = self.storage.get_user(user_id)
            if user and user.get('preferences'):
                user_preferences = user['preferences']

        # Override with explicit preferences
        if cuisine_preference:
            user_preferences['cuisine_preference'] = cuisine_preference
        if location:
            user_preferences['location'] = location
        if price_range:
            user_preferences['price_range'] = price_range
        if occasion:
            user_preferences['occasion'] = occasion

        # Get user preferences vector
        user_vector = self._get_user_preferences_vector(user_preferences)
        if user_vector is None:
            # If no preferences, return top-rated restaurants
            restaurants = self.storage.get_restaurants()
            return sorted(restaurants, key=lambda x: x['rating'], reverse=True)[:limit]

        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_vector, self.restaurant_vectors).flatten()
        
        # Get top restaurant indices
        top_indices = similarity_scores.argsort()[-limit:][::-1]
        
        # Get restaurant details
        recommendations = []
        for idx in top_indices:
            restaurant = self.storage.get_restaurant(self.restaurant_ids[idx])
            if restaurant:
                recommendations.append(restaurant)

        return recommendations

    def get_similar_restaurants(self, restaurant_id: int, limit: int = 5) -> List[Dict]:
        """Get restaurants similar to a given restaurant"""
        if not self.restaurant_vectors or not self.restaurant_ids:
            self._update_vectors()
            if not self.restaurant_vectors:
                return []

        # Find the index of the given restaurant
        try:
            restaurant_idx = self.restaurant_ids.index(restaurant_id)
        except ValueError:
            return []

        # Calculate similarity scores
        similarity_scores = cosine_similarity(
            self.restaurant_vectors[restaurant_idx:restaurant_idx+1],
            self.restaurant_vectors
        ).flatten()

        # Get top similar restaurant indices (excluding the input restaurant)
        top_indices = similarity_scores.argsort()[-limit-1:-1][::-1]
        
        # Get restaurant details
        similar_restaurants = []
        for idx in top_indices:
            restaurant = self.storage.get_restaurant(self.restaurant_ids[idx])
            if restaurant:
                similar_restaurants.append(restaurant)

        return similar_restaurants 