import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Restaurant Recommendations - AI-Powered Dining Discovery',
  description: 'Discover perfect restaurants with AI-powered recommendations. Get personalized suggestions based on your preferences, budget, and location.',
  keywords: 'restaurant recommendations, AI dining, food discovery, personalized suggestions',
  authors: [{ name: 'Restaurant Recommendation System' }],
  openGraph: {
    title: 'Restaurant Recommendations - AI-Powered Dining Discovery',
    description: 'Discover perfect restaurants with AI-powered recommendations',
    type: 'website',
    locale: 'en_US',
    siteName: 'Restaurant Recommendations',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Restaurant Recommendations - AI-Powered Dining Discovery',
    description: 'Discover perfect restaurants with AI-powered recommendations',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
