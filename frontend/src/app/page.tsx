import React from 'react';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import RestaurantCard from '@/components/RestaurantCard';
import DarkModeToggle from '@/components/DarkModeToggle';
import { BudgetBand } from '@/types';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">🍽️ ForkFinder</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/catalog" className="text-gray-700 dark:text-gray-300 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Browse
              </Link>
              <Link href="/recommendations" className="text-gray-700 dark:text-gray-300 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                Recommendations
              </Link>
              <DarkModeToggle />
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-primary-500 to-warning-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Find Your Perfect
              <br />
              <span className="text-primary-100">Dining Experience</span>
            </h1>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              AI-powered restaurant recommendations tailored to your taste, budget, and location
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/recommendations">
                <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold">
                  Get Recommendations
                </Button>
              </Link>
              <Link href="/catalog">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 text-lg font-semibold">
                  Explore Restaurants
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section with Advanced Effects */}
      <section className="py-16 bg-gray-50 dark:bg-gray-800 relative">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
              <span className="gradient-text">Why Choose Our Recommendations?</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Experience the future of restaurant discovery with cutting-edge AI technology
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="glassmorphism hover-lift p-6 rounded-2xl text-center group">
              <div className="bg-gradient-to-r from-primary-500 to-secondary-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 pulse-animation">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">AI-Powered</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Get personalized recommendations instantly with our fast and efficient recommendation engine
              </p>
            </div>
            <div className="glassmorphism hover-lift p-6 rounded-2xl text-center group">
              <div className="bg-gradient-to-r from-primary-500 to-secondary-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 pulse-animation">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Instant Results</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Receive immediate restaurant suggestions tailored to your preferences and location
              </p>
            </div>
            <div className="glassmorphism hover-lift p-6 rounded-2xl text-center group">
              <div className="bg-gradient-to-r from-primary-500 to-secondary-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 pulse-animation">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Personalized</h3>
              <p className="text-gray-600 dark:text-gray-300">
                Our AI learns from your preferences to provide better recommendations over time
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Recommendations with Advanced Effects */}
      <section className="py-16 bg-gradient-to-br from-gray-50 to-orange-50 dark:from-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
              <span className="gradient-text">Discover Amazing Restaurants</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Explore our curated selection of top-rated restaurants in your area
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <div className="hover-lift">
              <RestaurantCard
                restaurant={{
                  id: '1',
                  name: 'The Garden Terrace',
                  city: 'Bangalore',
                  cuisines: ['Continental', 'Italian'],
                  cost_band: BudgetBand.MEDIUM,
                  rating: 4.5,
                  tags: ['romantic', 'outdoor-seating'],
                                  }}
              />
            </div>
            <div className="hover-lift">
              <RestaurantCard
                restaurant={{
                  id: '2',
                  name: 'Spice Garden',
                  city: 'Delhi',
                  cuisines: ['North Indian', 'Mughlai'],
                  cost_band: BudgetBand.MEDIUM,
                  rating: 4.3,
                  tags: ['family-friendly', 'casual-dining'],
                                  }}
              />
            </div>
            <div className="hover-lift">
              <RestaurantCard
                restaurant={{
                  id: '3',
                  name: 'Sushi Master',
                  city: 'Mumbai',
                  cuisines: ['Japanese', 'Sushi'],
                  cost_band: BudgetBand.HIGH,
                  rating: 4.8,
                  tags: ['fine-dining', 'sushi-bar'],
                                  }}
              />
            </div>
          </div>

          <div className="text-center">
            <Link href="/catalog">
              <Button size="lg" className="bg-primary-600 text-white hover:bg-primary-700 px-8 py-4">
                View All Restaurants
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">41,665+</div>
              <div className="text-gray-600">Restaurants</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">154</div>
              <div className="text-gray-600">Cities</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">25+</div>
              <div className="text-gray-600">Cuisine Types</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">4.8★</div>
              <div className="text-gray-600">Avg Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-500 to-secondary-500 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Find Your Perfect Restaurant?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of food lovers who have discovered their favorite dining spots through our AI-powered recommendations
          </p>
          <Link href="/recommendations">
            <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 text-lg">
              Get Started Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">ForkFinder</h3>
              <p className="text-gray-400">
                AI-powered restaurant recommendations tailored to your taste and preferences.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/recommendations" className="hover:text-white">Get Recommendations</Link></li>
                <li><Link href="/catalog" className="hover:text-white">Browse Catalog</Link></li>
                <li><Link href="/status" className="hover:text-white">System Status</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Contact Us</a></li>
                <li><a href="#" className="hover:text-white">API Docs</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Connect</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Twitter</a></li>
                <li><a href="#" className="hover:text-white">Facebook</a></li>
                <li><a href="#" className="hover:text-white">Instagram</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 ForkFinder. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
