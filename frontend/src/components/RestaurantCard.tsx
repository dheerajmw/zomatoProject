import React from 'react';
import { Restaurant } from '@/types';
import { formatRating, formatEstimatedCost, truncateText } from '@/lib/utils';

interface RestaurantCardProps {
  restaurant: Restaurant;
  className?: string;
}

export default function RestaurantCard({ restaurant, className = '' }: RestaurantCardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-orange-100 ${className}`}>
      {/* Header with Rating - Orange/Amber Theme */}
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 p-4">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-1">
              {truncateText(restaurant.name, 30)}
            </h3>
            <div className="text-orange-100 text-sm font-medium">
              📍 {restaurant.city}
            </div>
          </div>
          <div className="bg-white/20 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm font-bold flex items-center">
            <span className="mr-1">⭐</span>
            {formatRating(restaurant.rating)}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Cuisines */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {restaurant.cuisines.slice(0, 3).map((cuisine, index) => (
              <span
                key={index}
                className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs font-semibold border border-orange-200"
              >
                {cuisine}
              </span>
            ))}
            {restaurant.cuisines.length > 3 && (
              <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-xs font-medium">
                +{restaurant.cuisines.length - 3}
              </span>
            )}
          </div>
        </div>

        {/* Cost Band */}
        <div className="mb-4">
          <div className="flex items-center text-gray-700 dark:text-gray-300">
            <span className="text-sm font-semibold">💰 {formatEstimatedCost(restaurant.cost_band)}</span>
          </div>
        </div>

        {/* Tags */}
        {restaurant.tags && restaurant.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-2">
              {restaurant.tags.slice(0, 2).map((tag, index) => (
                <span
                  key={index}
                  className="bg-amber-50 text-amber-700 px-3 py-1 rounded-lg text-xs font-medium border border-amber-200"
                >
                  {tag}
                </span>
              ))}
              {restaurant.tags.length > 2 && (
                <span className="bg-gray-100 text-gray-600 px-3 py-1 rounded-lg text-xs font-medium">
                  +{restaurant.tags.length - 2}
                </span>
              )}
            </div>
          </div>
        )}

        {/* AI Explanation */}
        {restaurant.explanation && (
          <div className="border-t border-gray-100 dark:border-gray-700 pt-4 mt-4">
            <div className="flex items-start">
              <span className="text-orange-500 mr-2 text-sm">🤖</span>
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                {truncateText(restaurant.explanation, 120)}
              </p>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <button className="w-full bg-gradient-to-r from-orange-500 to-amber-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-amber-600 transition-all duration-200 font-semibold text-sm shadow-md hover:shadow-lg">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}
