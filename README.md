
# Belgian betting arbitrage detector

## Description

### Goal
This project aims to identify arbitrage opportunities on Belgian sports betting websites for certain European leagues. Arbitrage situations in sports betting occur when a bettor can take advantage of differences in odds offered by different bookmakers to guarantee a profit regardless of the outcome of the event. In this project, we are focusing on identifying such opportunities for certain European leagues on Belgian sports betting websites.
### Implementation
This project aims to detect arbitrage situations in Belgian sports betting websites for selected European leagues. To achieve this, Python is used with the Selenium library, which allows for web scraping by instantiating a Chrome webdriver. One driver is created for each league, and the data is then structured and gathered together. There is no command line interface implemented yet, but the program can be run by specifying a config.json file and running bet_arbitrages/main.py. Currently, the project is deployed locally, and a Docker image builder is under construction.

Overall, the project involves web scraping, data structuring, and analysis of betting odds across different leagues. It also uses Python and the Selenium library for automation and scraping, and will be containerized using Docker for easier deployment and management. 

## Usage
Examples and instructions on how to use the project.


## License
Information about the license under which the project is released.

## Disclaimer
The goal of this project is solely for educational purposes and not for commercial or financial gain. The project aims to detect potential arbitrage situations on selected belgian sports betting websites. The project owner and contributors assume no liability for any financial losses or damages resulting from the use or misuse of the information and code provided. It is important to always gamble responsibly and within your means.

## Credit
Thanks to chat gpt who helps me to write this file.

## To Do
+ Let the container running and extracting data every m minutes
+ Fixing bugs which are quite random (*websites doesn't render data from time to time*) 
+ Functions to gather csv after each run into one database
+ Datatransformation --> Avoid repetition with datecolumn like *valid_from*, *valid_until*  
+ Some data analysis of the quotes
+ Bot who warns you when a surebet is possible
+ ???

