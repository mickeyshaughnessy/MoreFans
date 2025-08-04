# More Fans Platform API

## Overview

More Fans is a competitive platform where real-world teams compete to complete objectives while building fan engagement. Companies sponsor teams, fans follow and support their favorites, and everyone participates in a gamified ecosystem of real achievements.

### Key Features

- **Multi-layered Validation**: Combines manual review, automated verification, and community consensus
- **Real-time Engagement**: Live updates, predictions, and interactive fan experiences
- **Flexible Monetization**: Virtual currency, sponsorships, and premium subscriptions
- **Social Ecosystem**: Following, commenting, sharing, and team interactions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        More Fans API                         │
├─────────────────┬───────────────────┬───────────────────────┤
│   Core Services │  Real-time Layer  │  Integration Layer    │
├─────────────────┼───────────────────┼───────────────────────┤
│ • Auth/Users    │ • WebSocket Server │ • External APIs       │
│ • Teams         │ • Event Streaming  │ • IoT Devices         │
│ • Objectives    │ • Live Updates     │ • Payment Processing  │
│ • Validation    │ • Chat/Comments    │ • Media Storage       │
│ • Scoring       │ • Notifications    │ • Analytics           │
└─────────────────┴───────────────────┴───────────────────────┘
```

## API Endpoints

### Authentication & Users

```http
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/users/profile
PUT    /api/v1/users/profile
POST   /api/v1/users/upgrade-subscription
```

### Teams & Sponsors

```http
GET    /api/v1/teams
GET    /api/v1/teams/:teamId
POST   /api/v1/teams                    # Admin only
PUT    /api/v1/teams/:teamId           # Team admin only
POST   /api/v1/teams/:teamId/members   # Team admin only
DELETE /api/v1/teams/:teamId/members/:userId

GET    /api/v1/sponsors
POST   /api/v1/sponsors/:sponsorId/teams/:teamId  # Sponsorship request
PUT    /api/v1/sponsors/:sponsorId/teams/:teamId  # Update sponsorship
```

### Objectives & Submissions

```http
GET    /api/v1/objectives               # List active objectives
GET    /api/v1/objectives/:objectiveId
POST   /api/v1/objectives               # Admin only
PUT    /api/v1/objectives/:objectiveId  # Admin only

POST   /api/v1/objectives/:objectiveId/submissions
GET    /api/v1/submissions/:submissionId
PUT    /api/v1/submissions/:submissionId        # Add evidence
POST   /api/v1/submissions/:submissionId/review # Admin review
```

### Validation System

```http
# Admin Manual Review
POST   /api/v1/validation/admin/review
GET    /api/v1/validation/admin/pending

# Automated Validation
POST   /api/v1/validation/auto/configure
POST   /api/v1/validation/auto/webhook/:objectiveId
GET    /api/v1/validation/auto/status/:submissionId

# Community Verification
POST   /api/v1/validation/community/vote
GET    /api/v1/validation/community/pending
GET    /api/v1/validation/community/results/:submissionId
```

### Fan Engagement

```http
# Following/Social
POST   /api/v1/social/follow/teams/:teamId
DELETE /api/v1/social/follow/teams/:teamId
GET    /api/v1/social/following
POST   /api/v1/social/share
POST   /api/v1/social/comments
PUT    /api/v1/social/comments/:commentId
DELETE /api/v1/social/comments/:commentId

# Predictions & Voting
GET    /api/v1/predictions/active
POST   /api/v1/predictions/:predictionId/vote
GET    /api/v1/predictions/:predictionId/results

# Virtual Currency
GET    /api/v1/wallet/balance
POST   /api/v1/wallet/purchase
POST   /api/v1/wallet/transfer
GET    /api/v1/wallet/transactions
POST   /api/v1/wallet/tip/teams/:teamId
```

### Live Features

```http
GET    /api/v1/live/streams
GET    /api/v1/live/streams/:streamId
POST   /api/v1/live/streams             # Team only
DELETE /api/v1/live/streams/:streamId   # Team only

# WebSocket endpoints
WS     /ws/live/updates
WS     /ws/live/chat/:teamId
WS     /ws/live/notifications
```

## Data Models

### User
```json
{
  "userId": "uuid",
  "username": "string",
  "email": "string",
  "role": "fan|viewer|team_member|sponsor|admin",
  "subscriptionTier": "free|premium|vip",
  "walletBalance": 0,
  "followingTeams": ["teamId"],
  "achievements": ["achievementId"],
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
  "members": [
    {
      "userId": "uuid",
      "role": "leader|member",
      "joinedAt": "timestamp"
    }
  ],
  "sponsors": ["sponsorId"],
  "metrics": {
    "totalObjectivesCompleted": 0,
    "successRate": 0.95,
    "fanCount": 0,
    "totalEarnings": 0
  },
  "verified": true
}
```

### Objective
```json
{
  "objectiveId": "uuid",
  "title": "string",
  "description": "string",
  "category": "delivery|security|development|research",
  "validationType": {
    "manual": true,
    "automated": {
      "enabled": true,
      "endpoint": "https://api.example.com/verify",
      "requiredData": ["gpsLocation", "timestamp", "photo"]
    },
    "community": {
      "enabled": true,
      "minVotes": 100,
      "approvalThreshold": 0.7
    }
  },
  "rewards": {
    "points": 1000,
    "currency": 500,
    "achievements": ["achievementId"]
  },
  "deadline": "timestamp",
  "status": "active|completed|expired"
}
```

### Submission
```json
{
  "submissionId": "uuid",
  "objectiveId": "uuid",
  "teamId": "uuid",
  "evidence": {
    "description": "string",
    "photos": ["url"],
    "videos": ["url"],
    "data": {
      "gpsLocation": {"lat": 0, "lng": 0},
      "timestamp": "timestamp",
      "customFields": {}
    }
  },
  "validation": {
    "status": "pending|reviewing|approved|rejected",
    "adminReview": {
      "reviewerId": "uuid",
      "decision": "approved|rejected",
      "notes": "string",
      "timestamp": "timestamp"
    },
    "automatedCheck": {
      "status": "pending|passed|failed",
      "results": {},
      "timestamp": "timestamp"
    },
    "communityVotes": {
      "approve": 150,
      "reject": 20,
      "status": "voting|approved|rejected"
    }
  },
  "submittedAt": "timestamp"
}
```

## WebSocket Events

### Client → Server
```javascript
// Subscribe to updates
{
  "type": "subscribe",
  "channels": ["team:project-cobra", "objective:uuid", "global"]
}

// Send chat message
{
  "type": "chat",
  "teamId": "uuid",
  "message": "Go COBRA! 🐍"
}

// Live reaction
{
  "type": "reaction",
  "targetType": "submission|stream|team",
  "targetId": "uuid",
  "reaction": "🎉"
}
```

### Server → Client
```javascript
// New submission
{
  "type": "submission.new",
  "data": { /* submission object */ }
}

// Validation update
{
  "type": "validation.update",
  "data": {
    "submissionId": "uuid",
    "validationType": "admin|automated|community",
    "status": "approved|rejected",
    "details": {}
  }
}

// Live stream started
{
  "type": "stream.started",
  "data": {
    "streamId": "uuid",
    "teamId": "uuid",
    "title": "Working on Privacy Shield v2.0",
    "url": "rtmp://..."
  }
}

// Real-time metrics
{
  "type": "metrics.update",
  "data": {
    "teamId": "uuid",
    "metric": "fanCount|points|rank",
    "value": 1234,
    "change": +5
  }
}
```

## Authentication

### JWT Token Structure
```json
{
  "userId": "uuid",
  "role": "fan|viewer|team_member|sponsor|admin",
  "teamId": "uuid|null",
  "subscriptionTier": "free|premium|vip",
  "permissions": ["read", "write", "validate"],
  "exp": 1234567890
}
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>  # For external integrations
Content-Type: application/json
```

## Integration Examples

### External API Validation
```javascript
// Webhook endpoint for automated validation
app.post('/api/v1/validation/auto/webhook/:objectiveId', async (req, res) => {
  const { objectiveId } = req.params;
  const { submissionId, data } = req.body;
  
  // Verify webhook signature
  if (!verifyWebhookSignature(req)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process validation result
  await updateSubmissionValidation(submissionId, {
    type: 'automated',
    status: data.verified ? 'passed' : 'failed',
    results: data
  });
  
  // Trigger real-time update
  wsServer.broadcast('validation.update', {
    submissionId,
    validationType: 'automated',
    status: data.verified ? 'approved' : 'rejected'
  });
  
  res.json({ success: true });
});
```

### IoT Device Integration
```javascript
// Example: GPS tracker validation for delivery objective
const validateDeliveryLocation = async (submission) => {
  const { gpsLocation, timestamp } = submission.evidence.data;
  const objective = await getObjective(submission.objectiveId);
  
  // Check if GPS coordinates match target location
  const distance = calculateDistance(
    gpsLocation,
    objective.targetLocation
  );
  
  // Verify timing
  const timeDiff = new Date(timestamp) - new Date(objective.startTime);
  
  return {
    verified: distance < 100 && timeDiff > 0, // Within 100 meters
    details: {
      distance,
      timestamp,
      withinRange: distance < 100
    }
  };
};
```

### Community Voting Flow
```javascript
// Submit community vote
app.post('/api/v1/validation/community/vote', requireAuth, async (req, res) => {
  const { submissionId, vote } = req.body;
  const userId = req.user.userId;
  
  // Check if user has already voted
  const existingVote = await getVote(submissionId, userId);
  if (existingVote) {
    return res.status(400).json({ error: 'Already voted' });
  }
  
  // Record vote
  await recordVote(submissionId, userId, vote);
  
  // Check if threshold reached
  const results = await getVoteResults(submissionId);
  if (results.totalVotes >= MIN_VOTES) {
    const approvalRate = results.approve / results.totalVotes;
    if (approvalRate >= APPROVAL_THRESHOLD) {
      await updateSubmissionStatus(submissionId, 'approved');
    }
  }
  
  res.json({ success: true, results });
});
```

## Getting Started

### Installation
```bash
# Clone the repository
git clone https://github.com/more-fans/api.git

# Install dependencies
cd api
npm install

# Set up environment variables
cp .env.example .env

# Run database migrations
npm run migrate

# Start development server
npm run dev
```

### Environment Variables
```env
# Server
PORT=3000
NODE_ENV=development

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/morefans

# Authentication
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d

# Redis (for real-time features)
REDIS_URL=redis://localhost:6379

# External Services
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=morefans-media

# Streaming
RTMP_SERVER_URL=rtmp://stream.morefans.com/live

# Payment Processing
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# External Validation APIs
VALIDATION_API_KEY=xxx
IOT_PLATFORM_KEY=xxx
```

### Basic Usage Example
```javascript
import MoreFansSDK from '@morefans/sdk';

const sdk = new MoreFansSDK({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Authenticate
const { token } = await sdk.auth.login({
  email: 'fan@example.com',
  password: 'secure-password'
});

// Follow a team
await sdk.teams.follow('project-cobra');

// Make a prediction
await sdk.predictions.vote('prediction-123', {
  choice: 'team-cobra-wins',
  wager: 100 // Virtual currency
});

// Watch for real-time updates
sdk.realtime.subscribe(['team:project-cobra'], (event) => {
  console.log('New event:', event);
});
```

## Rate Limits

| Tier | Requests/Hour | WebSocket Connections | Stream Quality |
|------|--------------|---------------------|----------------|
| Free | 100 | 1 | 720p |
| Premium | 1000 | 5 | 1080p |
| VIP | 10000 | Unlimited | 4K |

## Support

- Documentation: https://docs.morefans.com
- API Status: https://status.morefans.com
- Support: support@morefans.com
- Discord: https://discord.gg/morefans

## License

MIT License - see LICENSE.md for details
