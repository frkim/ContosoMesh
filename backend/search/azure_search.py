"""
Azure AI Search integration for ContosoMesh products.
This module handles indexing and searching products using Azure AI Search.
"""

import os
import json
from typing import List, Optional, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from backend.models.schemas import Product

class AzureSearchService:
    def __init__(self):
        # These would normally come from environment variables
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "https://your-search-service.search.windows.net")
        self.search_key = os.getenv("AZURE_SEARCH_KEY", "your-search-key")
        self.index_name = "contoso-products"
        
        # For demo purposes, we'll use mock data if Azure credentials aren't available
        self.use_mock = not (self.search_endpoint.startswith("https://") and self.search_key != "your-search-key")
        
        if not self.use_mock:
            self.credential = AzureKeyCredential(self.search_key)
            self.search_client = SearchClient(
                endpoint=self.search_endpoint,
                index_name=self.index_name,
                credential=self.credential
            )
            self.index_client = SearchIndexClient(
                endpoint=self.search_endpoint,
                credential=self.credential
            )
    
    def create_index(self):
        """Create the search index for products."""
        if self.use_mock:
            print("Using mock search - Azure Search index creation skipped")
            return
        
        # Index definition would go here
        print("Azure Search index created (placeholder)")
    
    def index_products(self, products: List[Product]):
        """Index products in Azure AI Search."""
        if self.use_mock:
            # For demo, we'll store products in memory
            self._mock_products = products
            print(f"Mock indexed {len(products)} products")
            return
        
        # Convert products to search documents
        documents = []
        for product in products:
            doc = {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "features": " ".join(product.features),
                "specifications": json.dumps(product.specifications),
                "searchable_content": f"{product.name} {product.description} {' '.join(product.features)}"
            }
            documents.append(doc)
        
        try:
            result = self.search_client.upload_documents(documents)
            print(f"Indexed {len(documents)} products successfully")
            return result
        except Exception as e:
            print(f"Error indexing products: {e}")
            return None
    
    def search_products(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search products using Azure AI Search."""
        if self.use_mock:
            return self._mock_search(query, filters)
        
        try:
            # Build search options
            search_options = {
                "search_text": query,
                "top": 20,
                "include_total_count": True
            }
            
            if filters:
                filter_expressions = []
                if "category" in filters:
                    filter_expressions.append(f"category eq '{filters['category']}'")
                if "min_price" in filters:
                    filter_expressions.append(f"price ge {filters['min_price']}")
                if "max_price" in filters:
                    filter_expressions.append(f"price le {filters['max_price']}")
                if "in_stock" in filters and filters["in_stock"]:
                    filter_expressions.append("stock gt 0")
                
                if filter_expressions:
                    search_options["filter"] = " and ".join(filter_expressions)
            
            results = self.search_client.search(**search_options)
            
            # Convert to list for easier handling
            products = []
            for result in results:
                products.append(dict(result))
            
            return products
            
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def _mock_search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Mock search functionality for demo purposes."""
        if not hasattr(self, '_mock_products'):
            return []
        
        results = []
        query_lower = query.lower() if query else ""
        
        for product in self._mock_products:
            # Simple text matching
            if not query or (
                query_lower in product.name.lower() or
                query_lower in product.description.lower() or
                query_lower in product.category.lower() or
                any(query_lower in feature.lower() for feature in product.features)
            ):
                # Apply filters
                if filters:
                    if "category" in filters and product.category != filters["category"]:
                        continue
                    if "min_price" in filters and product.price < filters["min_price"]:
                        continue
                    if "max_price" in filters and product.price > filters["max_price"]:
                        continue
                    if "in_stock" in filters and filters["in_stock"] and product.stock <= 0:
                        continue
                
                # Convert to dict format similar to Azure Search results
                result = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                    "features": " ".join(product.features),
                    "specifications": json.dumps(product.specifications),
                    "@search.score": 1.0  # Mock relevance score
                }
                results.append(result)
        
        # Sort by relevance (mock)
        results.sort(key=lambda x: x["@search.score"], reverse=True)
        return results[:20]  # Limit to top 20
    
    def get_product_suggestions(self, partial_query: str) -> List[str]:
        """Get product name suggestions for autocomplete."""
        if self.use_mock:
            if not hasattr(self, '_mock_products'):
                return []
            
            suggestions = []
            partial_lower = partial_query.lower()
            
            for product in self._mock_products:
                if partial_lower in product.name.lower():
                    suggestions.append(product.name)
            
            return suggestions[:10]
        
        # Azure Search autocomplete would go here
        return []