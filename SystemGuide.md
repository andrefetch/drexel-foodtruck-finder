# Minimum Hardware and Software Requirements
TBD. Must be able to run a browser such as google chrome, edge, etc. No internet connection required.

# Installation Guide
To run the project locally:

1. Clone the Repository

```bash
git clone https://gitlab.cci.drexel.edu/cid/2526/ws1023/62/gc3/drexel-food-truck-interactive-map.git
cd drexel-food-truck-interactive-map
```

2. Have an Active Virtual Environment

## If you don't already have the environment set up

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows Powershell**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**Mac / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

## If you just need to run the virtual environment (you don't see the (venv) tag soon after starting the terminal)

**Windows**
```bash
venv\Scripts\activate
```

**Windows Powershell**
```bash
venv\Scripts\Activate.ps1
```

**Mac / Linux**
```bash
source venv/bin/activate
```

3. Install Dependencies
Make sure your virtual environment is active so all dependencies are installed there

```bash
pip install -r requirements.txt
```

4. Running the Project

**Windows / Windows Powershell**
```bash
python run.py
```

**Mac / Linux**
```bash
python3 run.py
```

Once you run the above code, in your terminal, you should see the below:

* Running on http://xxx.x.x.x:xxxx
* Running on http://xx.xxx.xxx.xx:xxxx

Hold ctrl and click on either link. The website will open to the "Home" page.

# Upkeep

## Seeding and Database Upkeep
The database gets updated when you run the seed python file. To seed, run the below code:

**Windows / Windows Powershell**
```bash
python seed.py
```

**Mac / Linux**
```bash
python seed.py
```

This pushes any data from the .csv files into the database. To update the .csv files, you must know that each food truck has an id associated with it. The id number is the order they appear in for data/foodtrucks.csv (i.e. Nanu's Hot Chicken is truck_id=1, Chicken Land is truck_id=2, etc.). In the three files found in the data directory, you can fill in information for a given food truck split into three files. Then, this is made into a truck object and put into the database with a given id.

## Navigating the Database
Food trucks are given an ID in an INTEGER format, name and cuisine both in VARCHAR(100) (strings with 100 characters max) where cuisine is allowed to be null, latitude and longitude are in FLOAT format, description is in the TEXT format (string with no character limit), and is_hidden is in the BOOLEAN format (false if it should appear on the map, true if not). For hours, they have an ID and day attached (where ID is the same as before, and day is an integer with 0 being Monday and 6 being Sunday) along with the hours for that day in a TIME format (Hour:Minute:Second). For the menu items, each integer ID is tied to a VARCHAR(100) name for the item, a FLOAT for the price, and an integer truck_id for the truck the item is sold at. When pulling this information through javascript, follow the fetch (as seen in map.js lines 120-188, focus on 120-128), and you can access each piece of info with an attribute call such as "truck.cuisine".

## Admin Page
The admin page allows you to access submitted trucks and accept/decline them. While menu/cuisine/time info has to be found by someone on the team, the location and name can be given by a user. To access this page, change the / at the end to "/admin". You will be prompted to log in, which can be found at {x}.

# Contact Info
Please reach out to us if you have any issues! You can send us an email, and expect a response in ~2-3 business days. Our contact info and roles are given below:

Andre Nunes da Silva, Fullstack Developer: an3243@drexel.edu
Alex Troeschel, Frontend Developer: at3698@drexel.edu
David Liberatore, Backend Developer: dal366@drexel.edu
Maisha Sultana, Website Developer: ms5529@drexel.edu

You can also find this information on the About page of the website. Please note that Kyle Cuba is no longer an active contributor to the project and should not be reached out to for information regarding the website.