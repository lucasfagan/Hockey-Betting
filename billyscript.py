from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
import requests
import json
import csv

# Get current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Go to the webpage with the current date
url = f'https://moneypuck.com/index.html?date={current_date}'

# Initialize the WebDriver for Safari
driver = webdriver.Safari()

# Load the webpage
driver.get(url)

# Get the page source
page_source = driver.page_source

# Parse the HTML content
soup = BeautifulSoup(page_source, 'html.parser')

# Find the element with selector path "#includedContent"
included_content = soup.select_one('#includedContent')

# Extract team logo links and winning percentages from the table
team_logo_links = [img['src'] for img in included_content.find_all('img')]
# Images are .../teamname.png, we want to extract the team name
team_names = [link.split('/')[-1].split('.')[0] for link in team_logo_links]

winning_percentages = [float(h2.text.strip()[:-1]) for h2 in included_content.find_all('h2')]

# Print the extracted data
# print("Team Names:")
# for name in team_names:
#     print(name)

# print("\nWinning Percentages:")
# for percentage in winning_percentages:
#     print(percentage)

# Close the WebDriver
driver.quit()

# API endpoint and parameters
url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/"
params = {
    "apiKey": "83ac7ed677aa12c75b9fb72001d91950",
    "regions": "us",
    "markets": "h2h",
}
team_abbreviations = {
    'Atlanta Flames': 'AFM',
    'Mighty Ducks of Anaheim': 'ANA',
    'Anaheim Ducks': 'ANA',
    'Arizona Coyotes': 'ARI',
    'Atlanta Thrashers': 'ATL',
    'Boston Bruins': 'BOS',
    'Brooklyn Americans': 'BRK',
    'Buffalo Sabres': 'BUF',
    'Carolina Hurricanes': 'CAR',
    'Columbus Blue Jackets': 'CBJ',
    'Bay Area Seals': 'CGS',
    'California Golden Seals': 'CGS',
    'Calgary Flames': 'CGY',
    'Chicago Black Hawks': 'CHI',
    'Chicago Blackhawks': 'CHI',
    'Cleveland Barons': 'CLE',
    'Colorado Rockies': 'CLR',
    'Colorado Avalanche': 'COL',
    'Dallas Stars': 'DAL',
    'Detroit Cougars': 'DCG',
    'Detroit Red Wings': 'DET',
    'Detroit Falcons': 'DFL',
    'Edmonton Oilers': 'EDM',
    'Florida Panthers': 'FLA',
    'Hamilton Tigers': 'HAM',
    'Hartford Whalers': 'HFD',
    'Kansas City Scouts': 'KCS',
    'Los Angeles Kings': 'LAK',
    'Minnesota Wild': 'MIN',
    'Montreal Maroons': 'MMR',
    'Minnesota North Stars': 'MNS',
    'Montréal Canadiens': 'MTL',
    'Montreal Wanderers': 'MWN',
    'New Jersey Devils': 'NJD',
    'Nashville Predators': 'NSH',
    'New York Americans': 'NYA',
    'New York Islanders': 'NYI',
    'New York Rangers': 'NYR',
    'California Seals': 'OAK',
    'Oakland Seals': 'OAK',
    'Ottawa Senators': 'OTT',
    'Philadelphia Flyers': 'PHI',
    'Phoenix Coyotes': 'PHX',
    'Pittsburgh Pirates': 'PIR',
    'Pittsburgh Penguins': 'PIT',
    'Quebec Bulldogs': 'QBD',
    'Philadelphia Quakers': 'QUA',
    'Quebec Nordiques': 'QUE',
    'Seattle Kraken': 'SEA',
    'Ottawa Senators (original)': 'SEN',
    'St Louis Eagles': 'SLE',
    'San Jose Sharks': 'SJS',
    'St Louis Blues': 'STL',
    'Toronto Hockey Club': 'TAN',
    'Toronto Arenas': 'TAN',
    'Tampa Bay Lightning': 'TBL',
    'Toronto Maple Leafs': 'TOR',
    'Toronto St. Patricks': 'TSP',
    'Vancouver Canucks': 'VAN',
    'Vegas Golden Knights': 'VGK',
    'Winnipeg Jets (original)': 'WIN',
    'Winnipeg Jets': 'WPG',
    'Washington Capitals': 'WSH'
}
# Make a GET request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_data = response.json()

    # Initialize an empty dictionary to store the parsed data
    team_odds = {}

    for data in response_data:

        # Iterate through the bookmakers in the response data
        for bookmaker in data['bookmakers']:
            # Iterate through the outcomes in the bookmaker's market data
            for outcome in bookmaker['markets'][0]['outcomes']:
                # Get the team name and price
                team_name, price = team_abbreviations[outcome['name']], outcome['price']
                
                # Add the team to the dictionary if it's not already there
                if team_name not in team_odds:
                    team_odds[team_name] = []
                
                # Add the betting site and price to the team's list
                team_odds[team_name].append([bookmaker['title'], price])

    # add winning percentages from above
    for i in range(len(team_names)):
        team_odds[team_names[i]].append(["Winning Percentage",winning_percentages[i]])

    # Create a set to store all unique betting sites
    betting_sites = set()
    for team in team_odds:
        for site in team_odds[team]:
            betting_sites.add(site[0])

    # Sort the betting sites for consistent column order
    betting_sites = sorted(list(betting_sites))

    # Define the CSV header
    header = ['Team name', 'Winning Percentage'] + betting_sites

    # Create the CSV file
    with open('team_data.csv', mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write the header
        csv_writer.writerow(header)
        
        # Write the data for each team
        for team in team_odds:
            # Create a dictionary with betting site as key and price as value
            site_prices = {site: price for site, price in team_odds[team]}
            
            # Prepare the row data
            row_data = [team, site_prices.get('Winning Percentage', '')]
            for site in betting_sites:
                row_data.append(site_prices.get(site, ''))
            
            # Write the row data
            csv_writer.writerow(row_data)

    print("CSV file created: team_data.csv")
else:
    print(response)