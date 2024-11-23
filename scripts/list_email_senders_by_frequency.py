import csv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from collections import Counter

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
MAX_LINES_PER_FILE = 500  # Define the max number of lines per CSV file

def save_to_csv(sorted_senders):
    """Save senders to multiple CSV files if the data exceeds the max lines per file."""
    file_count = 1
    lines_written = 0
    csv_file = open(f'senders_frequency_part{file_count}.csv', 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['Sender', 'Email Count'])  # Write header

    for sender, count in sorted_senders:
        if lines_written >= MAX_LINES_PER_FILE:
            # Close current file and start a new one
            csv_file.close()
            file_count += 1
            lines_written = 0
            csv_file = open(f'senders_frequency_part{file_count}.csv', 'w', newline='')
            writer = csv.writer(csv_file)
            writer.writerow(['Sender', 'Email Count'])  # Write header

        # Write sender and count
        writer.writerow([sender, count])
        lines_written += 1

    # Close the last file
    csv_file.close()
    print(f"Data saved into {file_count} file(s).")


def list_senders_by_frequency():
    # Authenticate and build Gmail service
    # The client secret file is obtained from the Google Cloud Console under OAuth 2.0 Client IDs in the project where the Gmail API is enabled. The associated email is jaditmustafa@gmail.com.    
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)

    # Fetch all messages
    senders = Counter()
    results = service.users().messages().list(userId='me', maxResults=500).execute()
    messages = results.get('messages', [])
    
    print("Fetching email metadata...")
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        for header in headers:
            if header['name'] == 'From':
                sender = header['value']
                senders[sender] += 1
                break

    # Sort senders by frequency (most frequent first)
    sorted_senders = senders.most_common()

    # Print sorted senders and counts
    print("\nSenders Ordered by Frequency:")
    for sender, count in sorted_senders:
        print(f"{sender}: {count}")

    # Save results to CSV
    save_to_csv(sorted_senders)


# Run the function
if __name__ == '__main__':
    list_senders_by_frequency()
