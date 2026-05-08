import React, { useState, useEffect } from 'react';
import { CatalogSummary } from '@/types';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import RestaurantAPI from '@/lib/api';

const CatalogPage: React.FC = () => {
  const [summary, setSummary] = useState<CatalogSummary | null>(null);
  const [restaurants, setRestaurants] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    location: '',
    cuisine_contains: '',
    minimum_rating: 0,
    budget: '',
    limit: 20
  });
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  useEffect(() => {
    loadCatalogSummary();
  }, []);

  const loadCatalogSummary = async () => {
    try {
      const data = await RestaurantAPI.getCatalogSummary();
      setSummary(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load catalog summary');
    }
  };

  const loadRestaurants = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await RestaurantAPI.getCatalogRestaurants(filters);
      setRestaurants(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load restaurants');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      location: '',
      cuisine_contains: '',
      minimum_rating: 0,
      budget: '',
      limit: 20
    });
    setRestaurants([]);
  };

  const exportData = () => {
    const csvContent = [
      ['ID', 'Name', 'City', 'Cuisines', 'Rating', 'Cost Band', 'Tags'].join(','),
      ...restaurants.map(r => [
        r.id,
        r.name,
        r.city,
        `"${r.cuisines.join(', ')}"`,
        r.rating,
        r.cost_band,
        `"${r.tags?.join(', ') || ''}"`
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'restaurant_catalog.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-primary-600 text-white py-8">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">Restaurant Catalog</h1>
          <p className="text-primary-100">
            Browse and explore our complete restaurant database
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {summary.row_count?.toLocaleString()}
              </div>
              <div className="text-gray-600">Total Restaurants</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-success-600 mb-2">
                {summary.unique_cities}
              </div>
              <div className="text-gray-600">Cities</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-warning-600 mb-2">
                {summary.skipped_invalid_rows}
              </div>
              <div className="text-gray-600">Skipped Rows</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <div className="text-3xl font-bold text-secondary-600 mb-2">
                {summary.sample_cities?.length}
              </div>
              <div className="text-gray-600">Sample Cities</div>
            </div>
          </div>
        )}

        {/* Filters Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold">Filters</h2>
            <div className="flex gap-2">
              <Button variant="outline" onClick={clearFilters}>
                Clear Filters
              </Button>
              <Button variant="outline" onClick={exportData} disabled={restaurants.length === 0}>
                Export CSV
              </Button>
            </div>
          </div>

          <div className="grid md:grid-cols-5 gap-4 mb-6">
            <Input
              label="Location"
              placeholder="Enter city..."
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
            />
            <Input
              label="Cuisine"
              placeholder="Cuisine type..."
              value={filters.cuisine_contains}
              onChange={(e) => handleFilterChange('cuisine_contains', e.target.value)}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Rating: {filters.minimum_rating}
              </label>
              <input
                type="range"
                min="0"
                max="5"
                step="0.5"
                value={filters.minimum_rating}
                onChange={(e) => handleFilterChange('minimum_rating', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            <Input
              label="Budget"
              placeholder="low/medium/high"
              value={filters.budget}
              onChange={(e) => handleFilterChange('budget', e.target.value)}
            />
            <Input
              label="Limit"
              type="number"
              min="1"
              max="100"
              value={filters.limit}
              onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
            />
          </div>

          <div className="flex justify-between items-center">
            <Button onClick={loadRestaurants} loading={loading}>
              {loading ? 'Loading...' : 'Search Restaurants'}
            </Button>
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'grid' ? 'primary' : 'outline'}
                onClick={() => setViewMode('grid')}
              >
                Grid View
              </Button>
              <Button
                variant={viewMode === 'table' ? 'primary' : 'outline'}
                onClick={() => setViewMode('table')}
              >
                Table View
              </Button>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6">
            <h3 className="text-error-800 font-medium mb-2">Error</h3>
            <p className="text-error-600">{error}</p>
          </div>
        )}

        {/* Results */}
        {restaurants.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">
                Results ({restaurants.length} restaurants)
              </h2>
            </div>

            {viewMode === 'grid' ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {restaurants.map((restaurant) => (
                  <div key={restaurant.id} className="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                    <h3 className="font-bold text-lg mb-2">{restaurant.name}</h3>
                    <p className="text-gray-600 text-sm mb-2">📍 {restaurant.city}</p>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {restaurant.cuisines?.slice(0, 3).map((cuisine: string, idx: number) => (
                        <span key={idx} className="bg-gray-100 px-2 py-1 rounded text-xs">
                          {cuisine}
                        </span>
                      ))}
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-green-600">⭐ {restaurant.rating}</span>
                      <span className="text-gray-600">💰 {restaurant.cost_band}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        City
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cuisines
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rating
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Cost
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tags
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {restaurants.map((restaurant) => (
                      <tr key={restaurant.id}>
                        <td className="px-6 py-4 whitespace-nowrap font-medium">
                          {restaurant.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {restaurant.city}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {restaurant.cuisines?.join(', ')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className="text-green-600">⭐ {restaurant.rating}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {restaurant.cost_band}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {restaurant.tags?.join(', ') || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* No Results */}
        {!loading && restaurants.length === 0 && !error && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-bold mb-2">No restaurants found</h3>
            <p className="text-gray-600">
              Try adjusting your filters or search criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CatalogPage;
