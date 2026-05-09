import React from 'react';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import RestaurantCard from '@/components/RestaurantCard';
import DarkModeToggle from '@/components/DarkModeToggle';

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900">
      {/* Dark Mode Toggle */}
      <div className="fixed top-4 right-4 z-50">
        <DarkModeToggle />
      </div>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Find Your Perfect
              <br />
              <span className="text-primary-200">Dining Experience</span>
            </h1>
            <p className="text-xl md:text-2xl mb-12 text-primary-100 max-w-2xl mx-auto">
              AI-powered restaurant recommendations tailored to your taste, budget, and location
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/recommendations">
                <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 text-lg">
                  Get Recommendations
                </Button>
              </Link>
              <Link href="/catalog">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-600 px-8 py-4 text-lg">
                  Explore Restaurants
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-16 bg-gray-50 dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Why Choose Our Recommendations?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
              <p className="text-gray-600">
                Advanced machine learning algorithms analyze your preferences to provide perfect restaurant matches
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Personalized</h3>
              <p className="text-gray-600">
                Tailored recommendations based on your location, budget, cuisine preferences, and dining history
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">Instant Results</h3>
              <p className="text-gray-600">
                Get personalized recommendations instantly with our fast and efficient recommendation engine
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Recommendations */}
      <section className="py-16 bg-gray-50 dark:bg-gray-800">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Discover Amazing Restaurants
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Explore our curated selection of top-rated restaurants in your area
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <RestaurantCard
              restaurant={{
                id: '1',
                name: 'The Garden Terrace',
                city: 'Bangalore',
                cuisines: ['Continental', 'Italian'],
                rating: 4.5,
                cost_band: 'medium',
                tags: ['romantic', 'outdoor seating'],
                explanation: 'Perfect for romantic dinners with authentic Italian cuisine and beautiful garden ambiance.'
              }}
            />
            <RestaurantCard
              restaurant={{
                id: '2',
                name: 'Spice Route',
                city: 'Delhi',
                cuisines: ['North Indian', 'Mughlai'],
                rating: 4.8,
                cost_band: 'high',
                tags: ['fine dining', 'authentic'],
                explanation: 'Experience authentic Mughlai flavors in an elegant setting with impeccable service.'
              }}
            />
            <RestaurantCard
              restaurant={{
                id: '3',
                name: 'Coastal Delights',
                city: 'Mumbai',
                cuisines: ['Seafood', 'Goan'],
                rating: 4.3,
                cost_band: 'medium',
                tags: ['seafood', 'casual'],
                explanation: 'Fresh coastal cuisine with a focus on Goan flavors and sustainable seafood.'
              }}
            />
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
