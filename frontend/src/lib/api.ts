import axios, { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { UserPreferences, RecommendationResponse, DisplayAPIResponse, CatalogSummary, MetricsSummary, APIError } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error: any) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: any) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class RestaurantAPI {
  // Phase 2: Validate user preferences
  static async validatePreferences(preferences: UserPreferences): Promise<UserPreferences> {
    try {
      const response = await api.post('/preferences', preferences);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 4: Get recommendations
  static async getRecommendations(
    preferences: UserPreferences,
    candidateCap: number = 50,
    topK?: number
  ): Promise<RecommendationResponse> {
    try {
      const params = new URLSearchParams();
      params.append('candidate_cap', candidateCap.toString());
      if (topK) {
        params.append('top_k', topK.toString());
      }

      const response = await api.post(`/recommendations?${params}`, preferences);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 5: Get display-ready response
  static async getDisplayResponse(
    preferences: UserPreferences,
    candidateCap: number = 50,
    topK?: number,
    includeHtml: boolean = true
  ): Promise<DisplayAPIResponse> {
    try {
      const params = new URLSearchParams();
      params.append('candidate_cap', candidateCap.toString());
      if (topK) {
        params.append('top_k', topK.toString());
      }
      params.append('include_html', includeHtml.toString());

      const response = await api.post(`/phase5/display?${params}`, preferences);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 1: Catalog endpoints
  static async getCatalogSummary(): Promise<CatalogSummary> {
    try {
      const response = await api.get('/catalog/summary');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getCatalogColumns(): Promise<{ columns: string[] }> {
    try {
      const response = await api.get('/catalog/columns');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getCatalogRestaurants(params: {
    location?: string;
    cuisine_contains?: string;
    minimum_rating?: number;
    budget?: string;
    limit?: number;
  }): Promise<any[]> {
    try {
      const searchParams = new URLSearchParams();
      Object.keys(params).forEach((key: string) => {
        const value = params[key as keyof typeof params];
        if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });

      const response = await api.get(`/catalog/restaurants?${searchParams}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 3: Integration endpoints
  static async getCandidates(preferences: UserPreferences, candidateCap: number = 50): Promise<any> {
    try {
      const response = await api.post(`/phase3/candidates?candidate_cap=${candidateCap}`, preferences);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getLLMContext(preferences: UserPreferences, candidateCap: number = 50): Promise<{ context: string }> {
    try {
      const response = await api.post(`/phase3/llm-context?candidate_cap=${candidateCap}`, preferences);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 5: Display endpoints
  static async getLoadingState(): Promise<any> {
    try {
      const response = await api.get('/phase5/loading');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getDemoPage(): Promise<string> {
    try {
      const response = await api.get('/phase5/demo');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Phase 6: Operations endpoints
  static async getMetrics(hours: number = 24): Promise<MetricsSummary> {
    try {
      const response = await api.get(`/phase6/metrics?hours=${hours}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getMetricsExport(hours: number = 24): Promise<any> {
    try {
      const response = await api.get(`/phase6/metrics/export?hours=${hours}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getSafetyStatus(): Promise<any> {
    try {
      const response = await api.get('/phase6/safety/status');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async runTests(phase?: string): Promise<any> {
    try {
      const params = phase ? `?phase=${phase}` : '';
      const response = await api.post(`/phase6/tests/run${params}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async createSnapshots(phase?: string): Promise<any> {
    try {
      const params = phase ? `?phase=${phase}` : '';
      const response = await api.post(`/phase6/tests/snapshots${params}`);
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getHealth(): Promise<any> {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  static async getPhase6Health(): Promise<any> {
    try {
      const response = await api.get('/phase6/health');
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  // Error handling
  private static handleError(error: any): APIError {
    if (error.response?.data) {
      const errorData = error.response.data;
      
      // Handle FastAPI validation errors
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          return {
            code: 'API_ERROR',
            message: errorData.detail,
          };
        } else if (typeof errorData.detail === 'object') {
          return {
            code: errorData.detail.code || 'VALIDATION_ERROR',
            message: errorData.detail.message || 'Validation failed',
            suggestions: errorData.detail.suggestions,
            details: errorData.detail,
          };
        }
      }
      
      return {
        code: 'API_ERROR',
        message: errorData.message || errorData.error || 'Unknown API error',
        details: errorData,
      };
    }
    
    if (error.code === 'ECONNABORTED') {
      return {
        code: 'TIMEOUT',
        message: 'Request timed out. Please try again.',
      };
    }
    
    if (error.code === 'NETWORK_ERROR') {
      return {
        code: 'NETWORK_ERROR',
        message: 'Network error. Please check your connection.',
      };
    }
    
    return {
      code: 'UNKNOWN_ERROR',
      message: error.message || 'An unexpected error occurred.',
    };
  }
}

export default RestaurantAPI;
