import os
import requests

def download_papers(subject, start_year=2009, end_year=2025, dest_folder=None):
    if dest_folder is None:
        dest_folder = f'{subject}_papers'
    
    print(f"Starting download for {subject} from {start_year} to {end_year}")
    base_url = f"https://www.bsebstudy.com/papers/bihar-board-class-12-{subject}-{{}}.pdf"
    os.makedirs(dest_folder, exist_ok=True)
    print(f"Created/verified folder: {dest_folder}")

    for year in range(start_year, end_year + 1):
        url = base_url.format(year)
        # Create abbreviated subject names for file naming
        subject_abbrev = {
            'biology': 'bio',
            'chemistry': 'chem',
            'physics': 'phy',
            'english': 'eng',
            'hindi': 'hin',
            'mathematics': 'math'
        }
        
        filename = os.path.join(dest_folder, f'{subject_abbrev[subject]}_{year}.pdf')
        
        # Check if file already exists
        if os.path.exists(filename):
            print(f'File for {year} already exists: {filename}')
            continue
        
        print(f'Downloading {year} from {url} ... ')
        
        # Try up to 3 times
        for attempt in range(1, 4):
            try:
                print(f'  Attempt {attempt}/3... ', end='')
                response = requests.get(url, timeout=10)
                print(f"Status: {response.status_code}, Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status_code == 200 and response.headers.get('Content-Type','').startswith('application/pdf'):
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print('Success')
                    break  # Success, exit retry loop
                else:
                    print(f'Failed (status {response.status_code})')
                    if attempt == 3:
                        print(f'  All attempts failed for year {year}')
                    
            except requests.RequestException as e:
                print(f'Error: {e}')
                if attempt == 3:
                    print(f'  All attempts failed for year {year}')

if __name__ == '__main__':
    print("Available subjects: biology, chemistry, physics, english, hindi, mathematics")
    subject = input("Enter the subject you want to download: ").lower().strip()
    
    # Validate subject input
    valid_subjects = ['biology', 'chemistry', 'physics', 'english', 'hindi', 'mathematics']
    if subject not in valid_subjects:
        print(f"Invalid subject. Please choose from: {', '.join(valid_subjects)}")
        exit(1)
    
    print(f"Script is running for {subject}...")
    download_papers(subject)
    print("Script completed.")
