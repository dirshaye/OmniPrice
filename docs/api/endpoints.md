# API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.omnipricex.com`

## Authentication

All endpoints (except public ones) require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Products API

### List Products
```http
GET /products?page=1&limit=10&category=electronics
```

**Response:**
```json
{
  "items": [
    {
      "id": "product_id",
      "name": "Product Name",
      "sku": "SKU123",
      "category": "electronics",
      "price": 99.99,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 10
}
```

### Create Product
```http
POST /products
Content-Type: application/json

{
  "name": "New Product",
  "sku": "SKU456",
  "category": "electronics",
  "base_price": 129.99,
  "description": "Product description"
}
```

### Get Product
```http
GET /products/{product_id}
```

### Update Product
```http
PUT /products/{product_id}
Content-Type: application/json

{
  "name": "Updated Product Name",
  "price": 119.99
}
```

### Delete Product
```http
DELETE /products/{product_id}
```

## Pricing API

### Get Current Price
```http
GET /pricing/{product_id}/current
```

### Set Pricing Rule
```http
POST /pricing/rules
Content-Type: application/json

{
  "product_id": "product_id",
  "rule_type": "competitor_based",
  "parameters": {
    "margin_min": 0.15,
    "margin_max": 0.35,
    "competitor_threshold": 0.95
  }
}
```

## Competitors API

### List Competitors
```http
GET /competitors
```

### Track Competitor Product
```http
POST /competitors/track
Content-Type: application/json

{
  "competitor_name": "CompetitorCorp",
  "product_url": "https://competitor.com/product/123",
  "our_product_id": "product_id"
}
```

## Analytics API

### Get Revenue Report
```http
GET /analytics/revenue?start_date=2024-01-01&end_date=2024-01-31
```

### Get Performance Metrics
```http
GET /analytics/performance/{product_id}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "price",
      "issue": "must be positive number"
    }
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
