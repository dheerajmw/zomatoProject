import React from 'react';
import { RestaurantCard as RestaurantCardType } from '@/types';
import { formatRating, formatEstimatedCost } from '@/lib/utils';

interface RestaurantCardProps {
  restaurant: RestaurantCardType;
  showRank?: boolean;
  className?: string;
}

const RestaurantCard: React.FC<RestaurantCardProps> = ({ 
  restaurant, 
  showRank = true, 
  className = '' 
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden ${className}`}>
      <div className="p-6">
        {/* Header with rank and name */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">
              {restaurant.name}
            </h3>
            <p className="text-sm text-gray-600 flex items-center">
              📍 {restaurant.location}
            </p>
          </div>
          {showRank && (
            <div className="bg-primary-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
              #{restaurant.rank}
            </div>
          )}
        </div>

        {/* Cuisines */}
        <div className="flex flex-wrap gap-2 mb-4">
          {restaurant.cuisines.map((cuisine, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
            >
              {cuisine}
            </span>
          ))}
        </div>

        {/* Rating, cost, and other info */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4 text-sm">
            <span className="text-green-600 font-medium">
              ⭐ {restaurant.rating_display}
            </span>
            <span className="text-gray-600">
              💰 {formatEstimatedCost(restaurant.cost_band)}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            {restaurant.cost_band.charAt(0).toUpperCase() + restaurant.cost_band.slice(1)} Cost
          </div>
        </div>

        {/* Tags */}
        {restaurant.tags && restaurant.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {restaurant.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs"
              >
                {tag}
              </span>
            ))}
            {restaurant.tags.length > 3 && (
              <span className="text-gray-500 text-xs">
                +{restaurant.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* AI Explanation */}
        {restaurant.explanation && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-md">
            <p className="text-sm text-blue-800 italic">
              {restaurant.explanation}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RestaurantCard;
