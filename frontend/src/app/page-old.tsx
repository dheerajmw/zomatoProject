import React from 'react';
import Link from 'next/link';
import Button from '@/components/ui/Button';
import RestaurantCard from '@/components/RestaurantCard';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
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
              <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 text-lg">
                Get Recommendations
              </Button>
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-primary-600 px-8 py-4 text-lg">
                Explore Restaurants
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Why Choose Our Recommendations?
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
              <p className="text-gray-600">
                Advanced LLM technology provides personalized recommendations with detailed explanations
              </p>
            </div>
            <div className="text-center">
              <div className="bg-success-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Precise Matching</h3>
              <p className="text-gray-600">
                Smart filtering based on location, budget, cuisine preferences, and ratings
              </p>
            </div>
            <div className="text-center">
              <div className="bg-warning-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⭐</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Quality Assured</h3>
              <p className="text-gray-600">
                41,665+ restaurants with verified ratings and comprehensive information
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sample Recommendations */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Sample Recommendations
            </h2>
            <p className="text-gray-600">
              Get a glimpse of what our AI-powered system can recommend
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Sample restaurant cards */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Tumbites</h3>
                  <p className="text-sm text-gray-600">📍 Left From Ramdev Medical Bellandur</p>
                </div>
                <div className="bg-primary-500 text-white px-3 py-1 rounded-full text-sm">
                  #1
                </div>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">North Indian</span>
              </div>
              <div className="flex items-center gap-4 mb-4 text-sm">
                <span className="text-green-600 font-medium">⭐ 3.9 ⭐⭐⭐</span>
                <span className="text-gray-600">💰 ₹0-₹800</span>
              </div>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-md">
                <p className="text-sm text-blue-800 italic">
                  Perfect match for your preferences with excellent North Indian cuisine
                </p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Kerala Mess Upahar</h3>
                  <p className="text-sm text-gray-600">📍 Bellandur Out Ring Road</p>
                </div>
                <div className="bg-primary-500 text-white px-3 py-1 rounded-full text-sm">
                  #2
                </div>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Kerala</span>
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Biryani</span>
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">South Indian</span>
              </div>
              <div className="flex items-center gap-4 mb-4 text-sm">
                <span className="text-green-600 font-medium">⭐ 3.8 ⭐⭐⭐</span>
                <span className="text-gray-600">💰 ₹0-₹800</span>
              </div>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-md">
                <p className="text-sm text-blue-800 italic">
                  Authentic Kerala cuisine with great biryani options
                </p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Parathabox</h3>
                  <p className="text-sm text-gray-600">📍 Bellandur</p>
                </div>
                <div className="bg-primary-500 text-white px-3 py-1 rounded-full text-sm">
                  #3
                </div>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">Fast Food</span>
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">North Indian</span>
              </div>
              <div className="flex items-center gap-4 mb-4 text-sm">
                <span className="text-green-600 font-medium">⭐ 3.8 ⭐⭐⭐</span>
                <span className="text-gray-600">💰 ₹0-₹800</span>
              </div>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-md">
                <p className="text-sm text-blue-800 italic">
                  Quick service with delicious parathas and North Indian dishes
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link href="/recommendations">
              <Button size="lg">
                Get Your Personal Recommendations →
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-100">
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
              <div className="text-4xl font-bold text-primary-600 mb-2">6</div>
              <div className="text-gray-600">Development Phases</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600 mb-2">100%</div>
              <div className="text-gray-600">AI-Powered</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Find Your Perfect Restaurant?
          </h2>
          <p className="text-xl mb-8 text-primary-100">
            Get personalized recommendations in seconds
          </p>
          <Link href="/recommendations">
            <Button size="lg" variant="secondary">
              Start Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="mb-2">
            🍽️ Restaurant Recommendation System - Powered by AI
          </p>
          <p className="text-gray-400 text-sm">
            Built with Next.js, FastAPI, and Groq LLM
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
