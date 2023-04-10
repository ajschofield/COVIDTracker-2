import os
from pathlib import Path
import pandas as pd
import requests
from datetime import datetime
from plotnine import *
from yaspin import yaspin
import time

# VARIABLES AND INITIALISATION
global error_count
error_count = 0
url = "https://api.coronavirus.data.gov.uk/v2/data"

def getStats(metric):
  # Define the query parameters
  params = {
    "areaType": "nation",
    "areaName": "England",
    "metric": metric,
    "format": "json"
    }

  response = requests.get(url,params=params)
  if response.status_code == 200:
    data = response.json()

    date_metric = {}

    for item in data["body"]:
      date = item["date"]
      metric_data = item[metric]
      date_metric[date] = metric_data
    
    return date_metric
  
  else:
    print(f"Error: Unable to fetch data. Status code: {response.status_code}")
    return None

path = Path("stats/")

with yaspin(text=" Checking if 'stats' folder is present...", color="yellow") as spinner:
  time.sleep(1)
  if not os.path.exists(path):
      spinner.fail("✘")
      os.makedirs(path)
  else:
      spinner.ok("✔")

with yaspin(text=" Downloading COVID-19 daily cases...", color="yellow") as spinner:
  time.sleep(2)
  try:
    cases = getStats("newCasesBySpecimenDate")
  except Exception:
    spinner.fail("✘")
    error_count += 1
  else:
    spinner.ok("✔")

with yaspin(text=" Downloading COVID-19 daily deaths...", color="yellow") as spinner:
  try:
    deaths = getStats("newDailyNsoDeathsByDeathDate")
  except Exception:
    spinner.fail("✘")
    error_count += 1
  else:
    spinner.ok("✔")

path_2 = Path("graphs/")

with yaspin(text=" Checking if 'graphs' folder is present...", color="yellow") as spinner:
  time.sleep(1)
  if not os.path.exists(path_2):
      spinner.fail("✘")
      os.makedirs(path_2)
  else:
      spinner.ok("✔")

# Create DataFrames for deaths and cases
data_deaths = pd.DataFrame(deaths.items(), columns=["date", "newDailyNsoDeathsByDeathDate"])
data_deaths["date"] = pd.to_datetime(data_deaths["date"])
data_cases = pd.DataFrame(cases.items(), columns=["date", "newCasesBySpecimenDate"])
data_cases["date"] = pd.to_datetime(data_cases["date"])

date_today = datetime.now().strftime('%d-%m-%Y')

# Create the ggplot graph for cases
graph_cases = (
    ggplot(data_cases, aes(x="date", y="newCasesBySpecimenDate"))
    + geom_line()
    + labs(title=f"England COVID-19 Cases by Date", x="Date", y="Cases")
    + theme_minimal()
    + theme(axis_text_x=element_text(rotation=45, hjust=1))
    + scale_x_date(date_breaks = "21 days")
    + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan', show_legend=True)
    + stat_smooth(method='mavg', method_args={'window': 7}, color='blue')
    + theme(axis_text_x=element_text(rotation=45, hjust=1))
)

# Save the graph to a file
graph_cases.save(filename=('cases_daily_' + str(date_today)),path=path_2,height=6, width=25, units = 'in', dpi=1000, verbose = False)

# Create the ggplot graph for deaths
graph_deaths = (
    ggplot(data_deaths, aes(x="date", y="newDailyNsoDeathsByDeathDate"))
    + geom_line()
    + labs(title=f"England COVID-19 Deaths by Date", x="Date", y="Deaths")
    + theme_minimal()
    + theme(axis_text_x=element_text(rotation=45, hjust=1))
    + scale_x_date(date_breaks = "21 days")
    + stat_smooth(method='mavg', method_args={'window': 3}, color='cyan', show_legend=True)
    + stat_smooth(method='mavg', method_args={'window': 7}, color='blue')
    + theme(axis_text_x=element_text(rotation=45, hjust=1))
)

# Save the graph to a file
graph_deaths.save(filename=('deaths_daily_' + str(date_today)),path=path_2,height=6, width=25, units = 'in', dpi=1000, verbose = False)