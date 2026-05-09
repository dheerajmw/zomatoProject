import React from 'react';
import { Restaurant } from '@/types';
import { formatRating, formatEstimatedCost, truncateText } from '@/lib/utils';

interface RestaurantCardProps {
  restaurant: Restaurant;
  className?: string;
}

export default function RestaurantCard({ restaurant, className = '' }: RestaurantCardProps) {
  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-200 overflow-hidden ${className}`}>
      {/* Header with Rating */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 p-4">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-bold text-white mb-1">
            {truncateText(restaurant.name, 30)}
          </h3>
          <div className="bg-white text-primary-600 px-2 py-1 rounded-full text-sm font-semibold flex items-center">
            <span className="mr-1">⭐</span>
            {formatRating(restaurant.rating)}
          </div>
        </div>
        <div className="text-primary-100 text-sm">
          📍 {restaurant.city}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Cuisines */}
        <div className="mb-3">
          <div className="flex flex-wrap gap-1">
            {restaurant.cuisines.slice(0, 3).map((cuisine, index) => (
              <span
                key={index}
                className="bg-primary-100 text-primary-700 px-2 py-1 rounded-full text-xs font-medium"
              >
                {cuisine}
              </span>
            ))}
            {restaurant.cuisines.length > 3 && (
              <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                +{restaurant.cuisines.length - 3}
              </span>
            )}
          </div>
        </div>

        {/* Cost Band */}
        <div className="mb-3">
          <div className="flex items-center text-gray-700">
            <span className="text-sm font-medium">💰 {formatEstimatedCost(restaurant.cost_band)}</span>
          </div>
        </div>

        {/* Tags */}
        {restaurant.tags && restaurant.tags.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-1">
              {restaurant.tags.slice(0, 2).map((tag, index) => (
                <span
                  key={index}
                  className="bg-accent-100 text-accent-700 px-2 py-1 rounded text-xs"
                >
                  {tag}
                </span>
              ))}
              {restaurant.tags.length > 2 && (
                <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                  +{restaurant.tags.length - 2}
                </span>
              )}
            </div>
          </div>
        )}

        {/* AI Explanation */}
        {restaurant.explanation && (
          <div className="border-t border-gray-100 pt-3 mt-3">
            <div className="flex items-start">
              <span className="text-primary-500 mr-2 text-sm">🤖</span>
              <p className="text-sm text-gray-600 leading-relaxed">
                {truncateText(restaurant.explanation, 120)}
              </p>
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="mt-4 pt-3 border-t border-gray-100">
          <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors duration-200 font-medium text-sm">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}
