// User Preferences
export interface UserPreferences {
  location: string;
  budget: BudgetBand;
  cuisines: string[];
  minimum_rating: number;
  optional_tags: string[];
}

export enum BudgetBand {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

// Restaurant Data
export interface Restaurant {
  id: string;
  name: string;
  city: string;
  cuisines: string[];
  cost_band: BudgetBand;
  rating: number;
  tags: string[];
}

// Recommendation Response
export interface RecommendationItem {
  rank: number;
  restaurant_id: string;
  restaurant: Restaurant;
  explanation: string;
}

export interface RecommendationResponse {
  recommendations: RecommendationItem[];
  llm_used: boolean;
  message?: string;
}

// Phase 5 Display Response
export interface RestaurantCard {
  rank: number;
  name: string;
  cuisines: string[];
  rating: number;
  rating_display: string;
  cost_band: string;
  estimated_cost: string;
  explanation: string;
  tags: string[];
  location: string;
}

export interface DisplayResponse {
  success: boolean;
  message?: string;
  restaurants: RestaurantCard[];
  total_count: number;
  llm_used: boolean;
  search_metadata: Record<string, any>;
}

export interface DisplayAPIResponse {
  display: {
    status: 'success' | 'empty' | 'error';
    title?: string;
    restaurants: RestaurantCard[];
    metadata: {
      total_results: number;
      llm_used: boolean;
      llm_status: string;
    };
  };
  html?: {
    cards: string[];
    styles: string;
  };
  raw_recommendations?: RecommendationResponse;
}

// Catalog Data
export interface CatalogSummary {
  row_count: number;
  skipped_invalid_rows: number;
  unique_cities: number;
  sample_cities: string[];
}

// Phase 6 Metrics
export interface RequestMetrics {
  request_id: string;
  timestamp: string;
  endpoint: string;
  method: string;
  user_agent?: string;
  ip_address?: string;
  processing_time_ms: number;
  phase_timings: Record<string, number>;
  result_count: number;
  llm_used: boolean;
  error?: string;
}

export interface MetricsSummary {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_processing_time_ms: number;
  llm_usage_rate: number;
  top_endpoints: Array<{
    endpoint: string;
    count: number;
  }>;
  error_summary: Record<string, number>;
  time_range: {
    start: string;
    end: string;
  };
}

// App State
export interface AppState {
  userPreferences: UserPreferences | null;
  recommendations: RecommendationResponse | null;
  displayResponse: DisplayAPIResponse | null;
  loading: boolean;
  error: string | null;
  metrics: MetricsSummary | null;
  catalogSummary: CatalogSummary | null;
}

export type AppAction =
  | { type: 'SET_PREFERENCES'; payload: UserPreferences }
  | { type: 'SET_RECOMMENDATIONS'; payload: RecommendationResponse }
  | { type: 'SET_DISPLAY_RESPONSE'; payload: DisplayAPIResponse }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'SET_METRICS'; payload: MetricsSummary }
  | { type: 'SET_CATALOG_SUMMARY'; payload: CatalogSummary }
  | { type: 'CLEAR_ERROR' }
  | { type: 'RESET_STATE' };

// API Error
export interface APIError {
  code: string;
  message: string;
  suggestions?: string[];
  details?: any;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

// Form States
export interface FormState {
  values: UserPreferences;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}
