from __future__ import annotations

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.schemas import RecommendResponse, RecommendationItem, RestaurantRecord, BudgetBand


class DisplayError(Exception):
    """Raised when display formatting encounters an error."""
    pass


@dataclass
class RestaurantCard:
    """Formatted restaurant card for UI display."""
    rank: int
    name: str
    cuisines: List[str]
    rating: float
    cost_band: str
    estimated_cost: str
    explanation: str
    tags: List[str]
    location: str


@dataclass
class DisplayResponse:
    """Complete display response with UI-ready data."""
    success: bool
    message: Optional[str]
    restaurants: List[RestaurantCard]
    total_count: int
    llm_used: bool
    search_metadata: Dict[str, Any]


def _format_estimated_cost(cost_band: BudgetBand) -> str:
    """Convert cost band to estimated cost range."""
    cost_ranges = {
        BudgetBand.LOW: "₹0-₹800",
        BudgetBand.MEDIUM: "₹800-₹1500", 
        BudgetBand.HIGH: "₹1500+"
    }
    return cost_ranges.get(cost_band, "Price not available")


def _format_rating_display(rating: float) -> str:
    """Format rating for display with star indicator."""
    stars = "⭐" * min(int(rating), 5)
    return f"{rating} {stars}"


def format_restaurant_card(item: RecommendationItem) -> RestaurantCard:
    """Format a single recommendation item into a display-ready card."""
    try:
        restaurant = item.restaurant
        
        return RestaurantCard(
            rank=item.rank,
            name=restaurant.name,
            cuisines=restaurant.cuisines,
            rating=restaurant.rating,
            cost_band=restaurant.cost_band.value,
            estimated_cost=_format_estimated_cost(restaurant.cost_band),
            explanation=item.explanation,
            tags=restaurant.tags,
            location=restaurant.city,
        )
    except Exception as e:
        raise DisplayError(f"Failed to format restaurant card: {e}")


def format_recommendation_response(response: RecommendResponse) -> DisplayResponse:
    """Format Phase 4 response for Phase 5 display."""
    try:
        restaurant_cards = []
        for item in response.recommendations:
            card = format_restaurant_card(item)
            restaurant_cards.append(card)
        
        return DisplayResponse(
            success=len(response.recommendations) > 0,
            message=response.message,
            restaurants=restaurant_cards,
            total_count=len(response.recommendations),
            llm_used=response.llm_used,
            search_metadata={
                "has_llm_explanations": response.llm_used,
                "fallback_used": not response.llm_used and len(response.recommendations) > 0,
            }
        )
    except Exception as e:
        raise DisplayError(f"Failed to format recommendation response: {e}")


def format_recommendations_ui(display_response: DisplayResponse) -> Dict[str, Any]:
    """Create complete UI-ready response with HTML/CSS structure."""
    
    if not display_response.success and not display_response.restaurants:
        # Empty state
        return {
            "status": "empty",
            "title": "No restaurants found",
            "message": display_response.message or "No restaurants match your criteria. Try adjusting your filters.",
            "suggestions": [
                "Lower the minimum rating",
                "Try different cuisines", 
                "Expand the location area",
                "Adjust budget range"
            ],
            "actions": [
                {"text": "Modify Search", "action": "edit_preferences"},
                {"text": "View All Restaurants", "action": "browse_catalog"}
            ]
        }
    
    # Success state with restaurant cards
    restaurant_html_cards = []
    for card in display_response.restaurants:
        card_html = f"""
        <div class="restaurant-card" data-rank="{card.rank}">
            <div class="rank-badge">#{card.rank}</div>
            <div class="restaurant-info">
                <h3 class="restaurant-name">{card.name}</h3>
                <div class="cuisine-tags">
                    {"".join([f'<span class="cuisine-tag">{cuisine}</span>' for cuisine in card.cuisines])}
                </div>
                <div class="meta-info">
                    <span class="rating">{_format_rating_display(card.rating)}</span>
                    <span class="cost">{card.estimated_cost}</span>
                    <span class="location">📍 {card.location}</span>
                </div>
                {f'<div class="explanation">{card.explanation}</div>' if card.explanation else ''}
                {f'<div class="tags">{"".join([f"<span class=\\"tag\\">{tag}</span>" for tag in card.tags])}</div>' if card.tags else ''}
            </div>
        </div>
        """
        restaurant_html_cards.append(card_html.strip())
    
    return {
        "status": "success",
        "title": f"Top {display_response.total_count} Restaurant Recommendations",
        "metadata": {
            "total_results": display_response.total_count,
            "llm_used": display_response.llm_used,
            "llm_status": "AI-powered recommendations" if display_response.llm_used else "Deterministic ranking"
        },
        "restaurants": [
            {
                "rank": card.rank,
                "name": card.name,
                "cuisines": card.cuisines,
                "rating": card.rating,
                "rating_display": _format_rating_display(card.rating),
                "cost_band": card.cost_band,
                "estimated_cost": card.estimated_cost,
                "explanation": card.explanation,
                "tags": card.tags,
                "location": card.location
            }
            for card in display_response.restaurants
        ],
        "html_cards": restaurant_html_cards,
        "css_styles": _get_ui_styles(),
        "actions": [
            {"text": "New Search", "action": "new_search"},
            {"text": "Filter Results", "action": "refine_search"}
        ]
    }


def _get_ui_styles() -> str:
    """Return CSS styles for the restaurant recommendation UI."""
    return """
    .restaurant-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .restaurant-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .rank-badge {
        position: absolute;
        top: -10px;
        right: 20px;
        background: #ff6b35;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .restaurant-name {
        margin: 0 0 8px 0;
        color: #2c3e50;
        font-size: 1.4em;
        font-weight: 600;
    }
    
    .cuisine-tags {
        margin-bottom: 12px;
    }
    
    .cuisine-tag {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85em;
        margin-right: 6px;
        color: #495057;
    }
    
    .meta-info {
        display: flex;
        gap: 16px;
        margin-bottom: 12px;
        font-size: 0.9em;
    }
    
    .rating {
        color: #28a745;
        font-weight: 600;
    }
    
    .cost {
        color: #6c757d;
        font-weight: 500;
    }
    
    .location {
        color: #6c757d;
    }
    
    .explanation {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 12px;
        margin: 12px 0;
        border-radius: 0 6px 6px 0;
        font-style: italic;
        color: #495057;
    }
    
    .tags {
        margin-top: 8px;
    }
    
    .tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75em;
        margin-right: 4px;
    }
    
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #6c757d;
    }
    
    .empty-state h3 {
        color: #495057;
        margin-bottom: 16px;
    }
    
    .suggestions {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 16px;
        margin: 20px 0;
    }
    
    .action-buttons {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 24px;
    }
    
    .btn {
        padding: 10px 20px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.2s ease;
    }
    
    .btn-primary {
        background: #007bff;
        color: white;
    }
    
    .btn-primary:hover {
        background: #0056b3;
    }
    
    .btn-secondary {
        background: #6c757d;
        color: white;
    }
    
    .btn-secondary:hover {
        background: #545b62;
    }
    """


def create_loading_state() -> Dict[str, Any]:
    """Create loading state for async operations."""
    return {
        "status": "loading",
        "title": "Finding Perfect Restaurants...",
        "message": "Analyzing your preferences and searching for the best matches",
        "spinner": True,
        "progress_steps": [
            "Validating your preferences",
            "Searching restaurant database", 
            "Filtering by your criteria",
            "Ranking the best options"
        ]
    }


def create_error_state(error_message: str) -> Dict[str, Any]:
    """Create error state for failed operations."""
    return {
        "status": "error", 
        "title": "Something went wrong",
        "message": error_message,
        "actions": [
            {"text": "Try Again", "action": "retry"},
            {"text": "Contact Support", "action": "support"}
        ]
    }
