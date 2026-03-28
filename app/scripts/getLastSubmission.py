"""
Sanitized version of getLastSubmission.py - Parses contest data to find latest submissions.
"""
import json
import csv
import os


def parse_submissions(json_file_path, assignment_num, language='ru'):
    """
    Parse Codeforces contest JSON and extract latest submissions per handle.
    
    Args:
        json_file_path: Path to contest JSON file
        assignment_num: Assignment number for output folder
        language: Language filter for submissions
    
    Returns:
        list: List of submission records [handle, submission_id, passedTestCount]
    """
    with open(json_file_path) as json_file:
        data = json.load(json_file)
    
    # Get contest ID from filename
    contest_id = os.path.splitext(os.path.basename(json_file_path))[0]
    input_folder = os.path.join(f"Assignment{assignment_num}", contest_id)
    
    # Create input folder
    os.makedirs(input_folder, exist_ok=True)
    
    submissions = data.get('result', [])
    handle_to_submission = {}
    
    # Find latest submission for each handle
    for submission in submissions:
        handle = submission['author']['members'][0]['handle']
        submission_id = submission['id']
        points = submission['passedTestCount'] if submission['passedTestCount'] > 0 else 0
        verdict = submission.get('verdict', 'UNKNOWN')
        participant_type = submission['author'].get('participantType', '')
        
        # Only consider CONTESTANT submissions
        if participant_type == "CONTESTANT":
            if handle in handle_to_submission:
                if submission_id > handle_to_submission[handle]['id']:
                    handle_to_submission[handle] = {
                        'id': submission_id,
                        'passedTestCount': points,
                        'verdict': verdict
                    }
            else:
                handle_to_submission[handle] = {
                    'id': submission_id,
                    'passedTestCount': points,
                    'verdict': verdict
                }
    
    # Build CSV data
    csv_data = []
    for handle, data_l in handle_to_submission.items():
        latest_submission_id = data_l['id']
        points = data_l['passedTestCount']
        csv_data.append([handle, latest_submission_id, points])
    
    # Sort by handle for consistent output
    csv_data.sort(key=lambda x: x[0])
    
    # Write CSV
    csv_file_path = f'Assignment{assignment_num}/submissions.csv'
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Handle', 'latest submission id', 'passedTestCount'])
        writer.writerows(csv_data)
    
    print(f'Sorted CSV file saved as {csv_file_path}')
    return csv_data


if __name__ == "__main__":
    print("Usage: Provide contest JSON file path and assignment number")
    # parse_submissions("Assignment1/656462.json", 1)
