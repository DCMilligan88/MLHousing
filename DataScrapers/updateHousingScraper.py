# Dependencies: 
import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from splinter import Browser 
import requests
import pickle
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# Initialize Splinter
executable_path = {'executable_path': '/Users/DCMil/OneDrive/Desktop/Job Hunting/Repo Projects/MLHousing/Resources/chromedriver'}
browser = Browser('chrome', **executable_path, headless=True)

# Directing splinter to webpage
portlandMLS_url = 'https://www.portlandmlsdirect.com/cgi-bin/real?pge=newsearch&state=na&widget=true&sortby=price&area=Portland+%28City%29&price_lo=0&price_hi=100000000&tot_bed_lo=0&tot_bath_lo=0&htype=ALL'
browser.visit(portlandMLS_url)

# Create variables
tracker = 0
updated_links = []

# Create BeautifulSoup object
soupy = BeautifulSoup(browser.html, 'html.parser')

# Identify the number of pages of houses
number_of_pages = soupy.find(id='ia_btn_text').text
page_count = int(number_of_pages[5:])
print(page_count)

# Look going through all the pages of listings
for p in range(1, page_count):
    tracker += 1 
    
    # Identify all items in the gridview class
    viewgrid_all = soupy.find_all('div', class_='viewgrid')
    last_item = viewgrid_all[-1].get('id')
    viewgrid_count = int(last_item[8:]) + 1
    
    # Loop going through each home listing on a page
    for g in range(1, viewgrid_count):
        
        # Create BeautifulSoup object
        soupy = BeautifulSoup(browser.html, 'html.parser')
        
        # Click on each grid item
        elems = soupy.find('div', {'id':(f'viewgrid{g}')}).find('a')
        start_html = "https://www.portlandmlsdirect.com/"  
        link = start_html + elems['href']
        updated_links.append(link)
    
    # Go to next page
    browser.find_by_id("ia_btn_next").click()
    print(f'Completion Percentage: {round((tracker/page_count)*100, 1)}%')
    
print(len(updated_links))

# List of links of the data previously scrape
with open("../Resources/housing_linksUpdated.txt", "rb") as fp:   # Unpickling
    link_list = pickle.load(fp)

# Create variables
new_listings = []

# Find new listings 
for link in updated_links:
    if link in link_list:
        pass
    else:
        new_listings.append(link)
        link_list.append(link)
        
print(new_listings)

# Define variables
list_home_dict = []
loading_error_links = []
error_count = 0
bath = "BATH"
acres = "ACRES"
neighbor = "Neighborhood"

# Loop to iterate through all listing links
for links in new_listings: 
    try:
        # Navigate to webpages for each home
        browser.visit(links)
        soup = BeautifulSoup(browser.html, 'html.parser')

        # To categorize homes with 0 bedrooms
        if bath in soup.find_all('div', class_="lineitem")[0].text:
            # Scraping primary data 
            address = soup.find('div', id="ia_address").text.replace("\n","").replace("\t  ", "")
            price = int(soup.find('div', id="ia_price").text.strip().replace('$', '').replace(',',''))
            bedrooms = 0 
            bathrooms = int(soup.find_all('div', class_="lineitem")[0].text[0])
            square_feet = int(soup.find_all('div', class_="lineitem")[1].text.replace(
                                                            'SQFT', '').replace(',', ''))
        
        else:
            # Scraping primary data
            address = soup.find('div', id="ia_address").text.replace("\n","").replace("\t  ", "")
            price = int(soup.find('div', id="ia_price").text.strip().replace('$', '').replace(',',''))
            bedrooms = int(soup.find_all('div', class_="lineitem")[0].text[0])
            bathrooms = float(soup.find_all('div', class_="lineitem")[1].text[0])
            square_feet = int(soup.find_all('div', class_="lineitem")[2].text.replace(
                                                            'SQFT', '').replace(',', ''))
        
        home_type = soup.find_all('div', id="PropDetailItem")[5].text[12:].replace('\n', '')
        built = int(soup.find_all('div', id="PropDetailItem")[3].text[12:])
        
        # Deals with pages that don't mention lot size
        if acres in soup.find_all('div', class_="lineitem")[4].text:
            lot_size = float(soup.find_all('div', class_="lineitem")[4].text.replace('ACRES', ''))

        else:
            lot_size = np.NaN 

        # Deals with pages that don't mention neighborhood
        if neighbor == soup.find_all('div', id='areaitemTitle')[3].text:
            neighborhood = soup.find_all('div', id='areaitemValue')[3].text

        else:
            neighborhood = "unknown"
            
        county = soup.find_all('div', id='areaitemValue')[0].text
        city = soup.find_all('div', id='areaitemValue')[1].text
        zipcode = soup.find_all('div', id='areaitemValue')[2].text

        # Schools data
        HS = soup.find_all('div', id="PropDetailTitle")[0].find_all_next('div')[10].text
        MS = soup.find_all('div', id="PropDetailTitle")[0].find_all_next('div')[6].text
        ES = soup.find_all('div', id="PropDetailTitle")[0].find_all_next('div')[2].text

        # Create dictionary to hold data collected
        home_dict = {
                'address':address,
                'price':price,
                'home_type':home_type,
                'bedrooms':bedrooms,
                'bathrooms':bathrooms,
                'square_feet':square_feet,
                'built':built,
                'lot_size':lot_size,
                'neighborhood':neighborhood,
                'county':county,
                'city':city,
                'zipcode':zipcode,
                'high_school':HS,
                'middle_school':MS,
                'elementary_school':ES
            }
        print(home_dict)

        # Append dictionaries to a list
        list_home_dict.append(home_dict)
    
    # Handles errors and collect links which data was able to be pulled
    except Exception as e:
        print('-------------')
        loading_error_links.append(links)
        error_count += 1
        print(error_count, e)
        
        pass

browser.quit()

# Create a df, drop duplicates
new_housing_data_df = pd.DataFrame(list_home_dict)
new_housing_data_df.drop_duplicates(inplace=True)

# Combine new data, drop duplicates
scraped_data = pd.read_csv("../Resources/housingDataUpdated.csv")
data_combined = scraped_data.append(new_housing_data_df)
data_combined.drop_duplicates(inplace=True)

# Drop duplicates and save housing data
data_combined.to_csv("../Resources/housingDataUpdated.csv", index = False, header = True)

# Save updated list of links
with open("../Resources/housing_linksUpdated.txt", "wb") as fp:   #Pickling
    pickle.dump(link_list, fp)

print(data_combined.shape)

print(new_housing_data_df.shape)

# Clearing database and uploading all the data (including freshly scraped data)
Base = declarative_base()

# Create the Listings class.
class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    address = Column(String(255))
    price = Column(Integer)
    home_type = Column(String(255))
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_feet = Column(Integer)
    built = Column(Integer)
    lot_size = Column(Float)
    neighborhood = Column(String(255))
    county = Column(String(255))
    city = Column(String(255))
    zipcode = Column(Integer)
    high_school = Column(String(255))
    middle_school = Column(String(255))
    elementary_school = Column(String(255))

# Create the database connection.
database_path = "../Resources/housingUpdated.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
conn = engine.connect()
session = Session(bind=engine)

# Clear out current data in the database.
Base.metadata.drop_all(engine)

# Create a metadata layer that abstracts the database.
Base.metadata.create_all(engine)

# Insert data into the database.
for _, row in data_combined.iterrows():
    listing = Listing(
      address = row["address"],
      price = row["price"],
      home_type = row["home_type"],
      bedrooms = row["bedrooms"],
      bathrooms = row["bathrooms"],
      square_feet = row["square_feet"],
      built = row["built"],
      lot_size = row["lot_size"],
      neighborhood = row["neighborhood"],
      county = row["county"],
      city = row["city"],
      zipcode = row["zipcode"],
      high_school = row["high_school"],
      middle_school = row["middle_school"],
      elementary_school = row["elementary_school"]
      )
    session.add(listing)

# Commit all listings
session.commit()

# Close the session.
session.close()

# Close the connection.
conn.close()