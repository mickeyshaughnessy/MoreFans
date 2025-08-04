#!/usr/bin/env python3
"""
Test script for More Fans API
Run with: python test_api.py
"""

import requests
import json
import time

API_URL = 'http://localhost:5000/api'
FAN_USER_ID = "fan-user-123"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    headers = {'Content-Type': 'application/json'}
    
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.ok:
            print(f"✅ {method} {endpoint} - {description}")
            return response.json()
        else:
            print(f"❌ {method} {endpoint} - {response.status_code}: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return None

def run_tests():
    """Run all API tests"""
    print("🚀 Starting More Fans API Tests (No Auth)\n")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/health')
        if not response.ok:
            raise Exception("Server not healthy")
    except:
        print("❌ Server is not running. Start it with: python api_server.py")
        return
    
    # 1. Test Teams
    print("\n1️⃣ Testing Teams")
    
    teams = test_endpoint('GET', '/teams', description="Get all teams")
    if teams:
        print(f"   Found {len(teams)} teams")
    
    # Follow Project COBRA (assuming it exists from sample data)
    if teams and len(teams) > 0:
        team_id = teams[0]['teamId']
        test_endpoint('POST', f'/teams/{team_id}/follow?user_id={FAN_USER_ID}', 
                      description="Follow team")
        
        test_endpoint('DELETE', f'/teams/{team_id}/follow?user_id={FAN_USER_ID}', 
                      description="Unfollow team")
        
        test_endpoint('POST', f'/teams/{team_id}/follow?user_id={FAN_USER_ID}', 
                      description="Follow team again")
    
    # 2. Test Objectives
    print("\n2️⃣ Testing Objectives")
    
    objectives = test_endpoint('GET', '/objectives', description="Get active objectives")
    if objectives:
        print(f"   Found {len(objectives)} active objectives")
    
    # 3. Test Wallet
    print("\n3️⃣ Testing Wallet")
    
    balance = test_endpoint('GET', f'/wallet/balance?user_id={FAN_USER_ID}', 
                            description="Check wallet balance")
    if balance:
        print(f"   Current balance: {balance['balance']}")
    
    # Tip a team
    if teams and len(teams) > 0:
        tip_result = test_endpoint('POST', f'/teams/{teams[0]["teamId"]}/tip?user_id={FAN_USER_ID}', 
                                  data={'amount': 100}, 
                                  description="Tip team 100 coins")
        
        # Check new balance
        new_balance = test_endpoint('GET', f'/wallet/balance?user_id={FAN_USER_ID}', 
                                    description="Check new balance")
        if new_balance:
            print(f"   New balance: {new_balance['balance']}")
    
    print("\n✨ All tests completed!")

if __name__ == '__main__':
    run_tests()