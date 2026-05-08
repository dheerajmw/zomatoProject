# Google Stitch Prompt - Next.js Frontend for Restaurant Recommendation System

## Prompt for Google Stitch

```
You are an expert full-stack developer specializing in modern web applications. I need you to create a complete Next.js frontend for a restaurant recommendation system that integrates with a FastAPI backend.

## Project Context

I have a fully functional restaurant recommendation API with the following architecture:

### Backend API (FastAPI)
- **Base URL**: `http://localhost:8000`
- **Phases**: Complete system with Phases 0-6 implemented
- **Key Features**: 
  - Restaurant catalog with 41,665+ restaurants
  - AI-powered recommendations using Groq LLM
  - User preference validation
  - Responsive UI components via Phase 5
  - Comprehensive testing and monitoring (Phase 6)

### API Endpoints to Integrate

#### Core Recommendation Flow
1. **POST /preferences** - Validate user preferences
2. **POST /recommendations** - Get AI-powered recommendations
3. **POST /phase5/display** - Get formatted UI-ready responses

#### Supporting Endpoints
- **GET /catalog/summary** - Dataset statistics
- **GET /catalog/restaurants** - Browse catalog with filters
- **GET /phase5/loading** - Loading state component
- **GET /phase5/demo** - Complete demo page

#### Phase 6 (Operations)
- **GET /phase6/metrics** - System metrics
- **GET /phase6/safety/status** - Rate limiting status
- **POST /phase6/tests/run** - Run system tests

## Frontend Requirements

### Technology Stack
- **Framework**: Next.js 14+ with App Router
- **Styling**: Tailwind CSS for responsive design
- **State Management**: React Context + useReducer for complex state
- **Data Fetching**: Axios with React Query (TanStack Query)
- **UI Components**: Headless UI or custom components
- **TypeScript**: Full TypeScript implementation
- **Deployment**: Vercel-ready configuration

### Pages & Components Needed

#### 1. Home Page (`/`)
- Hero section with app description
- Quick search form (location, budget, cuisines)
- Featured restaurants carousel
- Call-to-action to recommendations

#### 2. Recommendations Page (`/recommendations`)
- **Preference Form**: 
  - Location input with autocomplete
  - Budget selector (Low/Medium/High)
  - Cuisine multi-select with chips
  - Rating slider (0-5)
  - Optional tags input
- **Results Display**:
  - Loading states during API calls
  - Restaurant cards with Phase 5 HTML/CSS integration
  - AI explanations with formatting
  - Sorting and filtering options
  - Pagination for large result sets

#### 3. Restaurant Detail Page (`/restaurant/[id]`)
- Full restaurant information
- Reviews and ratings
- Similar recommendations
- Map integration (optional)
- Share functionality

#### 4. Catalog Browser (`/catalog`)
- Advanced filtering interface
- Table/grid view toggle
- Export functionality
- Statistics dashboard

#### 5. System Status (`/status`)
- Live system metrics from Phase 6
- API health indicators
- Performance graphs
- Test results display

### UI/UX Requirements

#### Design System
- **Color Scheme**: Modern, food-themed palette
- **Typography**: Clean, readable fonts
- **Spacing**: Consistent 8pt grid system
- **Components**: Reusable component library
- **Animations**: Smooth transitions and micro-interactions

#### Responsive Design
- **Mobile-first** approach
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Touch-friendly** interactions on mobile
- **Progressive enhancement** for older browsers

#### Accessibility
- **WCAG 2.1 AA** compliance
- **Keyboard navigation** support
- **Screen reader** compatibility
- **ARIA labels** and semantic HTML

### Integration Details

#### API Integration Pattern
```typescript
// API service example
class RestaurantAPI {
  private baseURL = 'http://localhost:8000';
  
  async getRecommendations(preferences: UserPreferences) {
    const response = await fetch(`${this.baseURL}/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(preferences)
    });
    return response.json();
  }
  
  async getDisplayResponse(preferences: UserPreferences) {
    const response = await fetch(`${this.baseURL}/phase5/display`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(preferences)
    });
    return response.json();
  }
}
```

#### Phase 5 Integration Example
```typescript
// Using Phase 5 pre-formatted HTML/CSS
const RecommendationCard = ({ restaurant }: { restaurant: RestaurantCard }) => {
  return (
    <div 
      className="restaurant-card"
      dangerouslySetInnerHTML={{ 
        __html: restaurant.htmlCard // From Phase 5 response
      }}
    />
  );
};

// Or custom rendering with structured data
const CustomRecommendationCard = ({ restaurant }: { restaurant: RestaurantCard }) => {
  return (
    <div className="border rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-bold text-gray-800">{restaurant.name}</h3>
        <span className="bg-orange-500 text-white px-3 py-1 rounded-full text-sm">
          #{restaurant.rank}
        </span>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-3">
        {restaurant.cuisines.map(cuisine => (
          <span key={cuisine} className="bg-gray-100 px-2 py-1 rounded text-sm">
            {cuisine}
          </span>
        ))}
      </div>
      
      <div className="flex items-center gap-4 mb-3 text-sm">
        <span className="text-green-600">⭐ {restaurant.rating_display}</span>
        <span className="text-gray-600">💰 {restaurant.estimated_cost}</span>
        <span className="text-gray-600">📍 {restaurant.location}</span>
      </div>
      
      {restaurant.explanation && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-3 italic">
          {restaurant.explanation}
        </div>
      )}
    </div>
  );
};
```

#### State Management
```typescript
// Global state context
interface AppState {
  userPreferences: UserPreferences | null;
  recommendations: RecommendationResponse | null;
  loading: boolean;
  error: string | null;
  metrics: MetricsSummary | null;
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
}>({} as any);

// Reducer for complex state management
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_PREFERENCES':
      return { ...state, userPreferences: action.payload };
    case 'SET_RECOMMENDATIONS':
      return { ...state, recommendations: action.payload, loading: false };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    default:
      return state;
  }
};
```

### Performance & SEO

#### Next.js Optimizations
- **Static Generation**: ISR for catalog pages
- **Image Optimization**: Next.js Image component
- **Code Splitting**: Dynamic imports for heavy components
- **Caching**: React Query for API caching
- **Bundle Analysis**: Webpack Bundle Analyzer

#### SEO Requirements
- **Meta Tags**: Dynamic titles and descriptions
- **Structured Data**: JSON-LD for restaurants
- **Open Graph**: Social sharing cards
- **Sitemap**: Auto-generated sitemap.xml
- **Robots.txt**: Proper crawling instructions

### Testing Strategy

#### Unit Tests
- **Jest + React Testing Library**
- **Component testing** for all UI components
- **API mocking** for consistent test data
- **Accessibility testing** with axe-core

#### E2E Tests
- **Playwright** for cross-browser testing
- **User journey** testing
- **API integration** testing
- **Performance** testing with Lighthouse

### Deployment & DevOps

#### Environment Configuration
```typescript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_GROQ_API_KEY: process.env.NEXT_PUBLIC_GROQ_API_KEY,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

#### Vercel Configuration
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api_url",
    "NEXT_PUBLIC_GROQ_API_KEY": "@groq_api_key"
  }
}
```

## Deliverables

### 1. Complete Next.js Application
- Full TypeScript implementation
- Responsive design with Tailwind CSS
- API integration with all endpoints
- State management and error handling
- Loading states and user feedback

### 2. Component Library
- Reusable UI components
- Design system documentation
- Storybook integration
- TypeScript definitions

### 3. Testing Suite
- Unit tests for all components
- Integration tests for API calls
- E2E tests for user journeys
- Performance benchmarks

### 4. Documentation
- README with setup instructions
- API integration guide
- Component documentation
- Deployment guide

### 5. Deployment Ready
- Vercel configuration
- Environment variables setup
- CI/CD pipeline
- Performance optimization

## Success Criteria

1. **Functional Integration**: All API endpoints working correctly
2. **User Experience**: Smooth, intuitive interface with proper feedback
3. **Performance**: Fast loading times and smooth interactions
4. **Responsive**: Works perfectly on all device sizes
5. **Accessible**: Meets WCAG 2.1 AA standards
6. **Production Ready**: Deployable with proper configuration

## Technical Constraints

- **Browser Support**: Modern browsers (ES2020+)
- **Performance**: Core Web Vitals "Good" ratings
- **Security**: Proper CSP headers and XSS prevention
- **Scalability**: Handle 10,000+ concurrent users
- **Maintainability**: Clean, documented, testable code

Please generate a complete Next.js frontend that meets all these requirements and integrates seamlessly with our Phase 5 backend API.
```

## Quick Start Commands

```bash
# Create Next.js app
npx create-next-app@latest restaurant-frontend --typescript --tailwind --eslint --app

# Install dependencies
cd restaurant-frontend
npm install @tanstack/react-query axios
npm install -D @types/node

# Start development
npm run dev
```

## API Response Examples for Reference

### User Preferences Schema
```json
{
  "location": "Bhajanpura",
  "budget": "medium",
  "cuisines": ["North Indian", "Chinese"],
  "minimum_rating": 4.0,
  "optional_tags": ["online-order"]
}
```

### Phase 5 Display Response
```json
{
  "display": {
    "status": "success",
    "restaurants": [
      {
        "rank": 1,
        "name": "Restaurant Name",
        "cuisines": ["North Indian"],
        "rating_display": "4.2 ⭐⭐⭐⭐",
        "estimated_cost": "₹800-₹1500",
        "explanation": "Perfect match for your preferences..."
      }
    ],
    "metadata": {
      "total_results": 5,
      "llm_used": true,
      "llm_status": "AI-powered recommendations"
    }
  },
  "html": {
    "cards": ["<div class=\"restaurant-card\">...</div>"],
    "styles": ".restaurant-card { ... }"
  }
}
```

This prompt provides everything needed to create a production-ready Next.js frontend that integrates perfectly with our restaurant recommendation backend system.
