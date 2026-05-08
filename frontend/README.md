# Restaurant Recommendation System - Frontend

A modern, AI-powered restaurant recommendation frontend built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🤖 **AI-Powered Recommendations**: Get personalized restaurant suggestions using advanced LLM technology
- 🎯 **Smart Filtering**: Filter by location, budget, cuisine, ratings, and dietary preferences
- 📊 **Real-time Catalog**: Browse and explore our complete restaurant database
- 📈 **System Monitoring**: Live performance metrics and system health dashboard
- 📱 **Responsive Design**: Optimized for all devices and screen sizes
- ♿ **Accessibility**: WCAG 2.1 compliant with semantic HTML and ARIA support
- ⚡ **Performance**: Optimized with Next.js 14, React Query, and efficient caching

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Context API
- **Data Fetching**: React Query (TanStack Query)
- **HTTP Client**: Axios
- **UI Components**: Custom component library with Headless UI patterns
- **Icons**: Heroicons
- **Testing**: Jest + React Testing Library + Playwright
- **Deployment**: Vercel ready

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Configure your API URL and Groq API key
# Edit .env.local with your values
```

### Environment Variables

Create a `.env.local` file with the following variables:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
GROQ_API_KEY=your_groq_api_key_here

# Optional: Analytics and monitoring
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
```

### Running the Development Server

```bash
# Start the development server
npm run dev

# Open http://localhost:3000 in your browser
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── globals.css        # Global styles
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── recommendations/   # Recommendations page
│   │   ├── catalog/           # Catalog browser page
│   │   └── status/            # System status page
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── ...
│   │   └── RestaurantCard.tsx # Restaurant card component
│   ├── lib/
│   │   ├── api.ts             # API service layer
│   │   └── utils.ts           # Utility functions
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   └── assets/                # Static assets
├── public/                    # Public assets
├── package.json
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

## Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Testing
npm run test         # Run unit tests
npm run test:e2e     # Run E2E tests with Playwright
npm run test:watch   # Run tests in watch mode

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues
npm run type-check   # Run TypeScript type checking

# Deployment
npm run export       # Export static site
```

## API Integration

The frontend integrates with the FastAPI backend through a comprehensive API service layer:

### Key API Endpoints

- `POST /preferences` - Validate user preferences
- `POST /recommendations` - Get AI-powered recommendations
- `POST /phase5/display` - Get display-ready responses
- `GET /catalog/summary` - Get catalog statistics
- `GET /catalog/restaurants` - Browse restaurant catalog
- `GET /phase6/metrics` - Get system performance metrics
- `GET /phase6/safety/status` - Get rate limiting status

### API Service Layer

The `src/lib/api.ts` file provides a comprehensive API service layer with:

- Automatic error handling and retry logic
- Request/response interceptors
- Type-safe API methods
- Environment variable configuration

## Pages

### Home Page (`/`)
- Hero section with call-to-action
- Feature highlights
- Sample recommendations
- Statistics and social proof

### Recommendations (`/recommendations`)
- Interactive preference form
- Real-time AI recommendations
- Restaurant cards with detailed information
- Quick search templates

### Catalog Browser (`/catalog`)
- Full catalog search and filtering
- Grid and table view modes
- Export functionality
- Advanced filtering options

### System Status (`/status`)
- Real-time performance metrics
- System health monitoring
- Rate limiting status
- Test execution interface

## Component Library

### UI Components (`src/components/ui/`)

- **Button**: Versatile button component with variants and sizes
- **Input**: Form input with validation states
- **Card**: Reusable card container
- **Loading**: Loading indicators and spinners
- **Modal**: Modal dialog component
- **Toast**: Notification system

### Business Components

- **RestaurantCard**: Display restaurant information with AI explanations
- **PreferenceForm**: Interactive preference selection
- **MetricsDashboard**: System performance visualization
- **CatalogTable**: Data table with sorting and filtering

## Styling

### Design System

- **Colors**: Primary, secondary, success, warning, error palettes
- **Typography**: Inter font family with responsive sizing
- **Spacing**: Consistent spacing scale
- **Animations**: Smooth transitions and micro-interactions

### Tailwind Configuration

Extended Tailwind configuration with:
- Custom color palettes
- Animation keyframes
- Component classes
- Responsive breakpoints

## Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

### Test Coverage
- Component rendering and behavior
- API service methods
- Utility functions
- User interactions

## Performance Optimization

### Next.js Optimizations
- Image optimization with next/image
- Automatic code splitting
- Static site generation where applicable
- Client-side caching with React Query

### Bundle Optimization
- Tree shaking for unused dependencies
- Dynamic imports for heavy components
- Optimized font loading
- Minified production builds

## Accessibility

- Semantic HTML5 structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Focus management
- Color contrast compliance

## Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Static Export
```bash
# Generate static site
npm run export

# Deploy to any static hosting service
```

## Environment Configuration

### Development
- Local API server (http://localhost:8000)
- Hot module replacement
- Development tools and debugging

### Production
- API URL from environment variables
- Optimized builds
- Performance monitoring
- Error tracking

## Contributing

1. Follow the existing code style and conventions
2. Write tests for new features
3. Update documentation as needed
4. Use semantic commit messages
5. Ensure accessibility compliance

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API URL in environment variables
   - Check backend server status
   - Review CORS configuration

2. **Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript configuration
   - Verify all dependencies are installed

3. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check CSS imports in layout
   - Verify class names match Tailwind config

## License

This project is licensed under the MIT License.

## Support

For questions and support:
- Check the documentation
- Review the API documentation
- Open an issue on GitHub
