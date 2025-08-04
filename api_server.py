#!/usr/bin/env python3
"""
More Fans API Server
Simple Flask API with S3 backend for team competition platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import handlers

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET', 'mithrilmedia')
app.config['AWS_REGION'] = os.environ.get('AWS_REGION', 'us-east-1')

# This is a temporary user ID for all actions since authentication is removed.
# In a real app, this would be determined by a logged-in session.
FAN_USER_ID = "fan-user-123" 
SPONSOR_USER_ID = "sponsor-user-456"

# Auth endpoints are removed as requested.

# User endpoint to get the "fan" user
@app.route('/api/users/fan', methods=['GET'])
def get_fan_user():
    user = handlers.get_user(FAN_USER_ID)
    if user:
    # Remove password for safety, even without auth
        return jsonify({k: v for k, v in user.items() if k != 'password'})
    return jsonify({'error': 'Fan user not found'}), 404

# Team endpoints
@app.route('/api/teams', methods=['GET'])
def get_teams():
    teams = handlers.get_all_teams()
    # Add fan count
    for team in teams:
        team['fanCount'] = handlers.get_team_fan_count(team['teamId'])
    return jsonify(teams)

@app.route('/api/teams/<team_id>', methods=['GET'])
def get_team(team_id):
    team = handlers.get_team(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    team['fanCount'] = handlers.get_team_fan_count(team_id)
    return jsonify(team)

@app.route('/api/teams/<team_id>/follow', methods=['POST', 'DELETE'])
def handle_follow_team(team_id):
    user_id = request.args.get('user_id', FAN_USER_ID) # Get user_id from query params
    team = handlers.get_team(team_id)
    if not team:
        return jsonify({'error': 'Team not found'}), 404
    
    if request.method == 'POST':
        handlers.follow_team(user_id, team_id)
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        handlers.unfollow_team(user_id, team_id)
        return jsonify({'success': True})

@app.route('/api/teams/<team_id>/tip', methods=['POST'])
def tip_team(team_id):
    user_id = request.args.get('user_id', FAN_USER_ID) # Get user_id from query params
    data = request.get_json()
    amount = data.get('amount', 0)
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    user = handlers.get_user(user_id)
    team = handlers.get_team(team_id)
    if not user or not team:
        return jsonify({'error': 'User or Team not found'}), 404
    
    # Check balance
    if user['walletBalance'] < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Process tip
    handlers.process_tip(user_id, team_id, amount)
    
    return jsonify({
        'success': True,
        'message': f'Tipped {amount} to {team["name"]}'
    })

# Objective endpoints
@app.route('/api/objectives', methods=['GET'])
def get_objectives():
    objectives = handlers.get_active_objectives()
    return jsonify(objectives)

# Objective creation is now open to all roles (for this demo)
@app.route('/api/objectives', methods=['POST'])
def create_objective():
    data = request.get_json()
    objective = handlers.create_objective(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category'),
        rewards=data.get('rewards')
    )
    return jsonify(objective)

# Wallet endpoints
@app.route('/api/wallet/balance', methods=['GET'])
def get_balance():
    user_id = request.args.get('user_id', FAN_USER_ID)
    user = handlers.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'balance': user['walletBalance']})

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

# Initialize sample data on startup
@app.before_first_request
def initialize():
    handlers.initialize_sample_data(FAN_USER_ID, SPONSOR_USER_ID)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
