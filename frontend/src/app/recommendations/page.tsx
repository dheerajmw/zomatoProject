import React, { useState, useEffect } from 'react';
import { Restaurant, RecommendationResponse } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import RestaurantCard from '@/components/RestaurantCard';
import RestaurantAPI from '@/lib/api';

export default function RecommendationsPage() {
  const [preferences, setPreferences] = useState({
    location: '',
    budget: 'medium',
    cuisines: '',
    minimum_rating: 4.0,
    optional_tags: ''
  });
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (field: string, value: any) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
  };

  const getRecommendations = async () => {
    if (!preferences.location || !preferences.cuisines) {
      setError('Please fill in location and cuisines');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await RestaurantAPI.getRecommendations({
        location: preferences.location,
        budget: preferences.budget,
        cuisines: preferences.cuisines.split(',').map(c => c.trim()),
        minimum_rating: preferences.minimum_rating,
        optional_tags: preferences.optional_tags ? preferences.optional_tags.split(',').map(t => t.trim()) : []
      });
      
      setRecommendations(response);
    } catch (err: any) {
      setError(err.message || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const quickSearches = [
    { name: 'Date Night', location: 'Delhi', budget: 'high', cuisines: 'Italian, Continental', rating: 4.5 },
    { name: 'Family Dinner', location: 'Bangalore', budget: 'medium', cuisines: 'North Indian, Chinese', rating: 4.0 },
    { name: 'Quick Lunch', location: 'Mumbai', budget: 'low', cuisines: 'Fast Food, South Indian', rating: 3.5 },
    { name: 'Business Meeting', location: 'Gurgaon', budget: 'high', cuisines: 'Continental, Japanese', rating: 4.5 }
  ];

  const applyQuickSearch = (search: typeof quickSearches[0]) => {
    setPreferences({
      location: search.location,
      budget: search.budget,
      cuisines: search.cuisines,
      minimum_rating: search.rating,
      optional_tags: ''
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold text-center mb-4">
            Get Personalized Recommendations
          </h1>
          <p className="text-xl text-center text-primary-100 max-w-2xl mx-auto">
            Tell us your preferences and let our AI find the perfect restaurants for you
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Quick Search Templates */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Quick Search Templates</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickSearches.map((search, index) => (
              <button
                key={index}
                onClick={() => applyQuickSearch(search)}
                className="bg-white border border-gray-300 rounded-lg p-4 hover:border-primary-500 hover:shadow-md transition-all text-left"
              >
                <div className="font-semibold text-gray-900 mb-1">{search.name}</div>
                <div className="text-sm text-gray-600">
                  {search.location} • {search.cuisines} • {search.rating}⭐
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Preference Form */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Your Preferences</h2>
          
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <Input
              label="Location"
              placeholder="Enter city or area..."
              value={preferences.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Budget Range
              </label>
              <select
                value={preferences.budget}
                onChange={(e) => handleInputChange('budget', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="low">Low (Under ₹500)</option>
                <option value="medium">Medium (₹500-₃000)</option>
                <option value="high">High (Above ₹3000)</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <Input
              label="Cuisines"
              placeholder="e.g., North Indian, Chinese, Italian"
              value={preferences.cuisines}
              onChange={(e) => handleInputChange('cuisines', e.target.value)}
              helperText="Separate multiple cuisines with commas"
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Rating: {preferences.minimum_rating}⭐
              </label>
              <input
                type="range"
                min="1"
                max="5"
                step="0.5"
                value={preferences.minimum_rating}
                onChange={(e) => handleInputChange('minimum_rating', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1⭐</span>
                <span>5⭐</span>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <Input
              label="Optional Tags"
              placeholder="e.g., outdoor seating, family-friendly, romantic"
              value={preferences.optional_tags}
              onChange={(e) => handleInputChange('optional_tags', e.target.value)}
              helperText="Separate multiple tags with commas"
            />
          </div>

          <Button 
            onClick={getRecommendations}
            loading={loading}
            className="w-full md:w-auto bg-primary-600 text-white hover:bg-primary-700 px-8 py-3 text-lg"
          >
            {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6">
            <h3 className="text-error-800 font-medium mb-2">Error</h3>
            <p className="text-error-600">{error}</p>
          </div>
        )}

        {/* Results */}
        {recommendations && (
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Recommended Restaurants ({recommendations.recommendations.length})
              </h2>
              <div className="text-sm text-gray-600">
                Powered by AI • Generated in {recommendations.processing_time_ms || 'N/A'}ms
              </div>
            </div>

            {recommendations.recommendations.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-bold mb-2 text-gray-900">No restaurants found</h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your preferences or search criteria
                </p>
                <Button 
                  onClick={() => setRecommendations(null)}
                  variant="outline"
                >
                  Clear Results
                </Button>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recommendations.recommendations.map((restaurant, index) => (
                  <div key={restaurant.id || index} className="fade-in" style={{ animationDelay: `${index * 100}ms` }}>
                    <RestaurantCard restaurant={restaurant} />
                  </div>
                ))}
              </div>
            )}

            {recommendations.recommendations.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600">
                    Found {recommendations.total_candidates || 'N/A'} total candidates, 
                    showing top {recommendations.recommendations.length} recommendations
                  </div>
                  <Button 
                    onClick={() => setRecommendations(null)}
                    variant="outline"
                  >
                    Search Again
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
