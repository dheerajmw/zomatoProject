import React, { useState } from 'react';
import { UserPreferences, BudgetBand } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import RestaurantCard from '@/components/RestaurantCard';
import RestaurantAPI from '@/lib/api';

const RecommendationsPage: React.FC = () => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    location: '',
    budget: BudgetBand.MEDIUM,
    cuisines: [],
    minimum_rating: 4.0,
    optional_tags: []
  });
  
  const [cuisineInput, setCuisineInput] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const availableCuisines = [
    'North Indian', 'South Indian', 'Chinese', 'Italian', 'Mexican',
    'Thai', 'Japanese', 'Continental', 'Biryani', 'Kerala',
    'Bengali', 'Gujarati', 'Rajasthani', 'Mughlai', 'Fast Food'
  ];

  const availableTags = [
    'online-order', 'delivery', 'takeaway', 'dine-in',
    'family-friendly', 'quick-service', 'fine-dining',
    'vegetarian', 'non-vegetarian', 'vegan', 'gluten-free'
  ];

  const handleAddCuisine = (cuisine: string) => {
    if (!preferences.cuisines.includes(cuisine)) {
      setPreferences({
        ...preferences,
        cuisines: [...preferences.cuisines, cuisine]
      });
    }
  };

  const handleRemoveCuisine = (cuisine: string) => {
    setPreferences({
      ...preferences,
      cuisines: preferences.cuisines.filter(c => c !== cuisine)
    });
  };

  const handleAddTag = (tag: string) => {
    if (!preferences.optional_tags.includes(tag)) {
      setPreferences({
        ...preferences,
        optional_tags: [...preferences.optional_tags, tag]
      });
    }
  };

  const handleRemoveTag = (tag: string) => {
    setPreferences({
      ...preferences,
      optional_tags: preferences.optional_tags.filter(t => t !== tag)
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Get display-ready recommendations
      const response = await RestaurantAPI.getDisplayResponse(preferences, 50, 5, true);
      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = (location: string, budget: BudgetBand, cuisines: string[]) => {
    setPreferences({
      ...preferences,
      location,
      budget,
      cuisines
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-primary-600 text-white py-8">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Restaurant Recommendations</h1>
          <p className="text-primary-100">
            Get personalized restaurant recommendations powered by AI
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Preference Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-6">Your Preferences</h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Location */}
                <Input
                  label="Location"
                  placeholder="Enter city or area (e.g., Bangalore, Bellandur)"
                  value={preferences.location}
                  onChange={(e) => setPreferences({...preferences, location: e.target.value})}
                  required
                />

                {/* Budget */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Range
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {Object.values(BudgetBand).map((budget) => (
                      <button
                        key={budget}
                        type="button"
                        onClick={() => setPreferences({...preferences, budget})}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          preferences.budget === budget
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {budget.charAt(0).toUpperCase() + budget.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Rating */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Rating: {preferences.minimum_rating}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={preferences.minimum_rating}
                    onChange={(e) => setPreferences({...preferences, minimum_rating: parseFloat(e.target.value)})}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>2.5</span>
                    <span>5</span>
                  </div>
                </div>

                {/* Cuisines */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cuisines
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {preferences.cuisines.map((cuisine) => (
                      <span
                        key={cuisine}
                        className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm flex items-center gap-1"
                      >
                        {cuisine}
                        <button
                          type="button"
                          onClick={() => handleRemoveCuisine(cuisine)}
                          className="text-primary-500 hover:text-primary-700"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {availableCuisines.slice(0, 8).map((cuisine) => (
                      <button
                        key={cuisine}
                        type="button"
                        onClick={() => handleAddCuisine(cuisine)}
                        disabled={preferences.cuisines.includes(cuisine)}
                        className="text-xs bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed px-2 py-1 rounded"
                      >
                        {cuisine}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Optional Tags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Optional Tags
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {preferences.optional_tags.map((tag) => (
                      <span
                        key={tag}
                        className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm flex items-center gap-1"
                      >
                        {tag}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag)}
                          className="text-blue-500 hover:text-blue-700"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {availableTags.slice(0, 6).map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => handleAddTag(tag)}
                        disabled={preferences.optional_tags.includes(tag)}
                        className="text-xs bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed px-2 py-1 rounded"
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  loading={loading}
                  disabled={!preferences.location || preferences.cuisines.length === 0}
                  className="w-full"
                >
                  {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
                </Button>
              </form>

              {/* Quick Search Templates */}
              <div className="mt-6 pt-6 border-t">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Search</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => handleQuickSearch('Bellandur', BudgetBand.LOW, ['North Indian', 'Chinese'])}
                    className="w-full text-left text-xs bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded"
                  >
                    🍽️ Bellandur • Low Budget • North Indian, Chinese
                  </button>
                  <button
                    onClick={() => handleQuickSearch('Bangalore', BudgetBand.MEDIUM, ['Italian', 'Continental'])}
                    className="w-full text-left text-xs bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded"
                  >
                    🍝 Bangalore • Medium Budget • Italian, Continental
                  </button>
                  <button
                    onClick={() => handleQuickSearch('Delhi', BudgetBand.HIGH, ['Fine Dining', 'Mughlai'])}
                    className="w-full text-left text-xs bg-gray-50 hover:bg-gray-100 px-3 py-2 rounded"
                  >
                    🍴 Delhi • High Budget • Fine Dining, Mughlai
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {loading && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Finding perfect restaurants for you...</p>
              </div>
            )}

            {error && (
              <div className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6">
                <h3 className="text-error-800 font-medium mb-2">Error</h3>
                <p className="text-error-600">{error}</p>
              </div>
            )}

            {results && !loading && (
              <div>
                {results.display?.status === 'success' && (
                  <div>
                    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                      <h2 className="text-2xl font-bold mb-2">
                        {results.display.title}
                      </h2>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>📊 {results.display.metadata.total_results} results</span>
                        <span>🤖 {results.display.metadata.llm_status}</span>
                      </div>
                    </div>

                    <div className="space-y-6">
                      {results.display.restaurants.map((restaurant: any) => (
                        <RestaurantCard
                          key={restaurant.rank}
                          restaurant={restaurant}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {results.display?.status === 'empty' && (
                  <div className="bg-white rounded-lg shadow-md p-8 text-center">
                    <div className="text-6xl mb-4">🔍</div>
                    <h3 className="text-xl font-bold mb-2">No restaurants found</h3>
                    <p className="text-gray-600 mb-4">{results.display.message}</p>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h4 className="font-medium mb-2">Suggestions:</h4>
                      <ul className="text-left text-sm text-gray-600 space-y-1">
                        {results.display.suggestions?.map((suggestion: string, index: number) => (
                          <li key={index}>• {suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {results.display?.status === 'error' && (
                  <div className="bg-error-50 border border-error-200 rounded-lg p-8 text-center">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h3 className="text-xl font-bold mb-2">Something went wrong</h3>
                    <p className="text-gray-600">{results.display.message}</p>
                  </div>
                )}
              </div>
            )}

            {!results && !loading && (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="text-6xl mb-4">🍽️</div>
                <h3 className="text-xl font-bold mb-2">Ready to find restaurants?</h3>
                <p className="text-gray-600 mb-4">
                  Set your preferences and click "Get Recommendations" to see personalized suggestions
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;
