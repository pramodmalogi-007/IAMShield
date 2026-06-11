# IAMShield MongoDB Collections Schema

## Database: `iamshield`

### `categories` — 5 IAM domain categories
```json
{ "_id": "privileged", "name": "Privileged Access", "icon": "lock", "color": "#FFD700", "order": 1 }
```

### `questions` — 2 questions per category (10 total)
```json
{ "category": "privileged", "order": 1, "text": "Who are the privileged users?",
  "options": [{"value": "sysadmins", "label": "System Administrators"}] }
```

### `products` — 2 products per category (10 total)
```json
{ "id": "pam_enterprise", "name": "PAM Enterprise", "category": "privileged",
  "price": 24999, "description": "...", "features": ["Session Recording"],
  "score_weights": {"sysadmins": 9, "vault": 9} }
```

### `users` — Registered accounts (bcrypt password)
```json
{ "firstName": "John", "lastName": "Smith", "email": "john@acme.com",
  "password": "<bcrypt>", "organizationName": "Acme Corp", "createdAt": ISODate }
```

### `assessments` — Assessment results per user
```json
{ "userId": "<id>", "category": "privileged",
  "answers": {"1": "sysadmins", "2": "vault"},
  "results": [{"id": "pam_enterprise", "score": 92}], "createdAt": ISODate }
```

### `carts` — One cart document per user (upserted)
```json
{ "userId": "<id>",
  "items": [{"productId": "pam_enterprise", "productName": "PAM Enterprise", "price": 24999, "quantity": 1}],
  "updatedAt": ISODate }
```

### `orders` — Confirmed orders
```json
{ "orderId": "IMS-2024-AB12CD34", "userId": "<id>",
  "billing": {"companyName": "Acme Corp", "gstNumber": "22AAAAA0000A1Z5", "email": "...", "phone": "..."},
  "paymentMethod": "upi", "subtotal": 24999, "tax": 4499.82, "totalAmount": 29498.82,
  "status": "confirmed", "createdAt": ISODate }
```
