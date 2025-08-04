#!/usr/bin/env python3
"""
Data handlers for More Fans API
Uses S3 for persistent storage with JSON files
"""

import json
import boto3
from datetime import datetime
import uuid
import os
from botocore.exceptions import ClientError
import bcrypt

# S3 Configuration
S3_BUCKET = os.environ.get('S3_BUCKET', 'mithrilmedia')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize S3 client
try:
    s3_client = boto3.client('s3', region_name=AWS_REGION)
except:
    # For local development without AWS credentials
    s3_client = None
    print("Warning: S3 client not initialized. Using local storage.")

# Local cache for development
local_cache = {
    'users': {},
    'teams': {},
    'objectives': {},
    'submissions': {},
    'follows': {}
}

def _get_s3_key(collection, item_id=None):
    """Generate S3 key for storing data"""
    if item_id:
        return f"morefans/{collection}/{item_id}.json"
    return f"morefans/{collection}/_index.json"

def _read_from_s3(key):
    """Read JSON data from S3"""
    if not s3_client:
        # Use local cache for development
        parts = key.split('/')
        collection = parts[1]
        if len(parts) > 2 and parts[2] != '_index.json':
            item_id = parts[2].replace('.json', '')
            return local_cache.get(collection, {}).get(item_id)
        return list(local_cache.get(collection, {}).values())
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return None
        raise

def _write_to_s3(key, data):
    """Write JSON data to S3"""
    if not s3_client:
        # Use local cache for development
        parts = key.split('/')
        collection = parts[1]
        if len(parts) > 2 and parts[2] != '_index.json':
            item_id = parts[2].replace('.json', '')
            if collection not in local_cache:
                local_cache[collection] = {}
            local_cache[collection][item_id] = data
        return
    
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
    except Exception as e:
        print(f"Error writing to S3: {e}")

def _update_index(collection, item_id, operation='add'):
    """Update collection index in S3"""
    index_key = _get_s3_key(collection)
    index = _read_from_s3(index_key) or []
    
    if operation == 'add' and item_id not in index:
        index.append(item_id)
    elif operation == 'remove' and item_id in index:
        index.remove(item_id)
    
    _write_to_s3(index_key, index)

# User functions
def get_user(user_id):
    """Get user by ID"""
    return _read_from_s3(_get_s3_key('users', user_id))

def get_all_users():
    """Get all users"""
    user_ids = _read_from_s3(_get_s3_key('users')) or []
    users = []
    for user_id in user_ids:
        user = get_user(user_id)
        if user:
            users.append(user)
    return users

def create_user(user_id, email, username, role, password_hash=None):
    """Create new user"""
    user = {
        'userId': user_id,
        'email': email,
        'username': username,
        'role': role,
        'password': password_hash,
        'walletBalance': 1000,  # Starting balance
        'followingTeams': [],
        'createdAt': datetime.utcnow().isoformat()
    }
    
    _write_to_s3(_get_s3_key('users', user['userId']), user)
    _update_index('users', user['userId'])
    
    return user

# Team functions
def get_team(team_id):
    """Get team by ID"""
    return _read_from_s3(_get_s3_key('teams', team_id))

def get_all_teams():
    """Get all teams"""
    team_ids = _read_from_s3(_get_s3_key('teams')) or []
    teams = []
    for team_id in team_ids:
        team = get_team(team_id)
        if team:
            teams.append(team)
    return teams

def create_team(name, description=''):
    """Create new team"""
    team = {
        'teamId': str(uuid.uuid4()),
        'name': name,
        'slug': name.lower().replace(' ', '-'),
        'description': description,
        'members': [],
        'sponsors': [],
        'metrics': {
            'totalObjectivesCompleted': 0,
            'successRate': 0,
            'totalEarnings': 0
        },
        'verified': False,
        'createdAt': datetime.utcnow().isoformat()
    }
    
    _write_to_s3(_get_s3_key('teams', team['teamId']), team)
    _update_index('teams', team['teamId'])
    
    return team

def get_team_fan_count(team_id):
    """Get number of fans following a team"""
    users = get_all_users()
    return sum(1 for user in users if team_id in user.get('followingTeams', []))

# Follow functions
def follow_team(user_id, team_id):
    """User follows a team"""
    user = get_user(user_id)
    if not user:
        return False
    
    if team_id not in user.get('followingTeams', []):
        user['followingTeams'] = user.get('followingTeams', [])
        user['followingTeams'].append(team_id)
        _write_to_s3(_get_s3_key('users', user_id), user)
    
    return True

def unfollow_team(user_id, team_id):
    """User unfollows a team"""
    user = get_user(user_id)
    if not user:
        return False
    
    user['followingTeams'] = [t for t in user.get('followingTeams', []) if t != team_id]
    _write_to_s3(_get_s3_key('users', user_id), user)
    
    return True

# Wallet functions
def process_tip(user_id, team_id, amount):
    """Process a tip from user to team"""
    user = get_user(user_id)
    team = get_team(team_id)
    
    if not user or not team:
        return False
    
    # Deduct from user
    user['walletBalance'] -= amount
    _write_to_s3(_get_s3_key('users', user_id), user)
    
    # Add to team
    team['metrics']['totalEarnings'] += amount
    _write_to_s3(_get_s3_key('teams', team_id), team)
    
    return True

# Objective functions
def get_active_objectives():
    """Get all active objectives"""
    obj_ids = _read_from_s3(_get_s3_key('objectives')) or []
    objectives = []
    for obj_id in obj_ids:
        obj = _read_from_s3(_get_s3_key('objectives', obj_id))
        if obj and obj.get('status') == 'active':
            objectives.append(obj)
    return objectives

def create_objective(title, description='', category='general', rewards=None):
    """Create new objective"""
    objective = {
        'objectiveId': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'category': category,
        'rewards': rewards or {'points': 1000, 'currency': 500},
        'deadline': datetime(2025, 12, 31).isoformat(),
        'status': 'active',
        'createdAt': datetime.utcnow().isoformat()
    }
    
    _write_to_s3(_get_s3_key('objectives', objective['objectiveId']), objective)
    _update_index('objectives', objective['objectiveId'])
    
    return objective

def initialize_sample_data(fan_user_id, sponsor_user_id):
    """Initialize with sample data if empty"""
    users = get_all_users()
    if not any(user['userId'] == fan_user_id for user in users):
        create_user(fan_user_id, 'testfan@example.com', 'testfan', 'fan', None)
        create_user(sponsor_user_id, 'sponsor@example.com', 'sponsor', 'sponsor', None)
    
    teams = get_all_teams()
    if not teams:
        # Create Project COBRA
        cobra = create_team(
            'Project COBRA',
            'Protecting individual privacy in an increasingly connected digital world'
        )
        cobra['verified'] = True
        cobra['metrics']['successRate'] = 95
        _write_to_s3(_get_s3_key('teams', cobra['teamId']), cobra)
        
        # Create sample objective
        create_objective(
            'Privacy Shield Beta Test',
            'Deploy and test privacy protection software with 100 beta users',
            'development',
            {'points': 1000, 'currency': 500}
        )
        
        print("Sample data initialized")