

# More Fans Platform API

## Overview

More Fans is a competitive platform where real-world teams, like Project COBRA, compete to complete objectives while building fan engagement. Fans can follow teams, tip them with virtual currency, and track active objectives. The platform is designed to foster interaction between teams and their supporters in a gamified ecosystem.

### Key Features

- **Team Interaction**: Fans can follow/unfollow teams and tip them with virtual currency.
- **Objective Tracking**: View and create objectives for teams to complete.
- **Simple Storage**: Uses AWS S3 for persistent storage with JSON files.
- **Real-time Updates**: Basic polling-based frontend for team and objective updates.

## Architecture

```
┌───────────────────────────────┐
│         More Fans API         │
├───────────────────────────────┤
│ • Flask-based REST API        │
│ • AWS S3 Storage             │
│ • Frontend (HTML/JS/CSS)     │
│ • No Authentication (Demo)   │
└───────────────────────────────┘
```

## API Endpoints

### Users
```http
GET    /api/users/fan           # Get fan user details
```

### Teams
```http
GET    /api/teams               # List all teams
GET    /api/teams/:teamId      # Get specific team details
POST   /api/teams/:teamId/follow  # Follow a team
DELETE /api/teams/:teamId/follow  # Unfollow a team
POST   /api/teams/:teamId/tip    # Tip a team with virtual currency
```

### Objectives
```http
GET    /api/objectives          # List active objectives
POST   /api/objectives          # Create new objective
```

### Wallet
```http
GET    /api/wallet/balance      # Get user's wallet balance
```

### Health Check
```http
GET    /health                  # Check API status
```

## Data Models

### User
```json
{
  "userId": "uuid",
  "username": "string",
  "email": "string",
  "role": "fan|sponsor",
  "walletBalance": 1000,
  "followingTeams": ["teamId"],
  "createdAt": "timestamp"
}
```

### Team
```json
{
  "teamId": "uuid",
  "name": "Project COBRA",
  "slug": "project-cobra",
  "description": "string",
  "members": [],
  "sponsors": [],
  "metrics": {
    "totalObjectivesCompleted": 0,
    "successRate": 0,
    "totalEarnings": 0
  },
  "verified": true,
  "createdAt": "timestamp"
}
```

### Objective
```json
{
  "objectiveId": "uuid",
  "title": "string",
  "description": "string",
  "category": "general|development",
  "rewards": {
    "points": 1000,
    "currency": 500
  },
  "deadline": "timestamp",
  "status": "active",
  "createdAt": "timestamp"
}
```

## Getting Started

### Installation
```bash
# Clone the repository
git clone https://github.com/more-fans/api.git

# Install dependencies
cd api
pip install flask flask-cors boto3

# Set up environment variables
cp .env.example .env

# Start the server
python api_server.py
```

### Environment Variables
```env
# Server
PORT=5000
SECRET_KEY=dev-secret-change-in-production

# AWS S3
S3_BUCKET=mithrilmedia
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

### Running Tests
```bash
# Run API tests
python test_api.py
```

### Frontend
The frontend is a single HTML page (`index.html`) with JavaScript and CSS for:
- Displaying teams with follow/unfollow and tip functionality
- Listing active objectives
- Showing wallet balance
- Polling for updates every 30 seconds

Serve it with any static file server or open directly in a browser after starting the API server.

## Usage Example
```javascript
// Example API calls using fetch
async function main() {
  // Get all teams
  const teams = await fetch('http://localhost:5000/api/teams').then(res => res.json());

  // Follow a team
  await fetch(`http://localhost:5000/api/teams/${teams[0].teamId}/follow?user_id=fan-user-123`, {
    method: 'POST'
  });

  // Tip a team
  await fetch(`http://localhost:5000/api/teams/${teams[0].teamId}/tip?user_id=fan-user-123`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount: 100 })
  });

  // Get wallet balance
  const balance = await fetch('http://localhost:5000/api/wallet/balance?user_id=fan-user-123')
    .then(res => res.json());
  console.log('Balance:', balance.balance);
}
```

## Rate Limits
- No rate limits implemented in this demo version
- All users have equal access to API endpoints

## Support
- Contact: support@morefans.com
- Project COBRA: https://robotservicesauction.com/cobra

## License
MIT License - see LICENSE.md for details

