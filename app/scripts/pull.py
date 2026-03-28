"""
Sanitized version of pull.py - Fetches contest data from Codeforces API.
Remove private keys before committing to version control.
"""
import random
import hashlib
import operator
from collections import OrderedDict
import time
import requests
import json
import os


def generate_api_signature(method, params, secret):
    """Generate API signature for Codeforces API authentication."""
    rand = str(random.randint(100000, 999999))
    s = '{}/{}?'.format(rand, method)
    ordered_params = OrderedDict(sorted(params.items(), key=operator.itemgetter(0)))
    s += '&'.join(map(__key_value_to_http_parameter, ordered_params.items()))
    s += '#' + secret
    return rand + hashlib.sha512(s.encode()).hexdigest()


def __key_value_to_http_parameter(item):
    """Convert key-value pair to HTTP parameter string."""
    key, value = item
    return '{}={}'.format(key, value)


def fetch_contest_data(contest_id, api_key, secret, assignment_num):
    """
    Fetch contest submissions from Codeforces API.
    
    Args:
        contest_id: Codeforces contest ID
        api_key: Codeforces API key
        secret: Codeforces API secret
        assignment_num: Assignment number for folder organization
    
    Returns:
        dict: API response data or None on error
    """
    current_time = int(time.time())
    method = "contest.status"
    
    params = {
        "apiKey": api_key,
        "contestId": contest_id,
        "time": str(current_time),
        "asManager": "true"
    }
    
    api_signature = generate_api_signature(method, params, secret)
    link = (f"https://codeforces.com/api/{method}?"
            f"contestId={contest_id}&apiKey={api_key}"
            f"&asManager=true&time={current_time}&apiSig={api_signature}")
    
    try:
        response = requests.get(link, timeout=30)
        response.raise_for_status()
        
        # Create assignment folder if needed
        os.makedirs(f"Assignment{assignment_num}", exist_ok=True)
        
        # Save raw response
        output_path = f"Assignment{assignment_num}/{contest_id}.json"
        with open(output_path, "w") as outfile:
            json.dump(response.json(), outfile, indent=2)
        
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching contest data: {e}")
        return None


if __name__ == "__main__":
    # Example usage - replace with your own credentials
    print("This script requires Codeforces API credentials.")
    print("Please provide your API key and secret.")
    
    # CONTEST_ID = "YOUR_CONTEST_ID"
    # API_KEY = "YOUR_API_KEY"  # Do not hardcode!
    # SECRET = "YOUR_SECRET"    # Do not hardcode!
    # ASSIGNMENT = 1
    
    # data = fetch_contest_data(CONTEST_ID, API_KEY, SECRET, ASSIGNMENT)
    # if data:
    #     print(f"Fetched {len(data.get('result', []))} submissions")
