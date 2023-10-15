import re
import pandas as pd
import requests,urllib.request
import random
import time
from .config import queries
import threading 

import os

emailRegex = re.compile(r'''
#example :
#something-.+_@somedomain.com
(
([a-zA-Z0-9_.+]+
@
[a-zA-Z0-9_.+]+)
)
''', re.VERBOSE)
        
# Extacting Emails

def is_valid_email(email):
    # Regular expression pattern for a more comprehensive email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Check if the email matches the pattern
    return bool(re.match(pattern, email))

def extractEmailsFromUrlText(urlText):
    extractedEmail =  emailRegex.findall(urlText)
    allemails = []
    for email in extractedEmail:
        allemails.append(email[0])
    lenh = len(allemails)
    print("\tNumber of Emails : %s\n" % lenh)
    seen = set()
    emailString = ''
    for email in allemails:
        if email not in seen:
            seen.add(email)
            # emailList.append(email)
            if is_valid_email(email):
                emailString += email + ','
    
    if emailString=='':
        return 'No Emails Found'
    else:
        return emailString

# HtmlPage Read Func
def htmlPageRead(url):
    try:
        start = time.time()
        headers = { 'User-Agent' : ' /5.0' }
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        urlHtmlPageRead = response.read()
        urlText = urlHtmlPageRead.decode()
        print ("%s\tFetched in : %s" % ( url, (time.time() - start)))
        return extractEmailsFromUrlText(urlText)
    except:
        print("some error in link")
        return "Error Occurred"
    
# EmailsLeechFunction
def emailsLeechFunc(url):
    try:
        return htmlPageRead(url)
    except urllib.error.HTTPError as err:
        print("Error in Link Opening")
        if err.code == 404:
            try:
                url = 'http://webcache.googleusercontent.com/search?q=cache:' + url
                emailString=htmlPageRead(url)
                return emailString
            except:
                return "Error Occurred"
        else:
            return "Error Occurred"    


def optimize_code(fileName):
    start = time.time()
    csv_file_path = f'output/{fileName}.csv'
    print(csv_file_path)
    df=pd.DataFrame()
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
        print(df.head())
    else:
        print(f"Error: The CSV file '{csv_file_path}' does not exist.")
        return
    
    print("Started.....")

    # Prepare the headers for the requests
    headers = {'User-Agent': ' /5.0'}

    valid_email_rows = []
    all_rows = []
    for i, row in df.iterrows():
        email_string = emailsLeechFunc(row['website'])
        row['emails'] = email_string
        all_rows.append(row)
        if email_string != 'Error Occurred' and email_string != 'No Emails Found':
            valid_email_rows.append(row)

    # Create DataFrames for both valid email rows and all rows
    valid_email_df = pd.DataFrame(valid_email_rows)
    all_df = pd.DataFrame(all_rows)

    # Generate a random number and append it to the file names
    random_number = random.randint(1000, 9999)
    valid_email_file_name = f'/{fileName}-valid-emails-{random_number}.csv'
    all_file_name = f'/{fileName}-all-emails-{random_number}.csv'

    # Save the DataFrames to separate CSV files with random number appended to file names

    # Construct the path to the output directory relative to the current file's directory
    output_dir = os.path.join(os.path.dirname(__file__), "../output/withEmail")

    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)    

    valid_email_df.to_csv(output_dir+valid_email_file_name, index=False)
    all_df.to_csv(output_dir+all_file_name, index=False)
    print("Elapsed Time: %s" % (time.time() - start))


def thread_function(query):
    name = query['keyword'].split(" ")
    name = [x.lower() for x in name]
    name = "-".join(name)

    optimize_code(name)

    print(name + " Done...")

def ScrapeEmailTask():
    threads = []
    for query in queries:
        thread = threading.Thread(target=thread_function, args=(query,))
        threads.append(thread)
        thread.start()

    start_time = time.time()
    for thread in threads:
        thread.join(timeout=600)  # Wait for thread to complete or timeout after 10 minutes
        if thread.is_alive():
            print("Thread not completed within 10 minutes, terminating...")
            # You might set a flag inside optimize_code to exit gracefully
            # thread.do_exit = True

    print("Total Elapsed Time: %s" % (time.time() - start_time))


