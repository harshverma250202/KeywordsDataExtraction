from bose.launch_tasks import launch_tasks
from bose import LocalStorage
from src import tasks_to_be_run
import time
from src.EmailScrapperWithConfig import ScrapeEmailTask


if __name__ == "__main__":
    print("Started Scrapping Website links from Google Maps...........")
    launch_tasks(*tasks_to_be_run)
    
    print("Finished Scrapping Website links from Google Maps...........")
    print("Started Scrapping Emails from Websites...........")
    time.sleep(5)
    ScrapeEmailTask()
    print("Finished Scrapping Emails from Websites...........")
    
    

