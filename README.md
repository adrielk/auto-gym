# auto-gym

Auto - Gym is an automated gym reservation scheudling program that uses the [Selenium Webdriver](https://selenium-python.readthedocs.io/installation.html) for the [AFC weight room](https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf) at the University of Virginia. Since the start of the COVID school year, there is a strict capacity limit on how many people can be in the AFC weight room at once. Spots fill up quickly and it can be easy to forget when to schedule a time. This program can be run once and take care of weight room reservations for you by automatically detecting when spots open up and reserving your spot!

## How to Run

To run this program, you need to install [ChromeDriver](https://chromedriver.chromium.org/) and **pip install selenium**. Place the chromedriver executable in the same directory as this program. If running on Raspberry Pi, follow this [ChromeDriver installation guide](https://ivanderevianko.com/2020/01/selenium-chromedriver-for-raspberrypi) 

This program is called on the command line as follows:

`python auto_gym.py username password time days`


## Example:

`python auto_gym.py fake_username fake_password "4:30 PM" 1,2,3,4,5,6,7`

Note: 1 = Monday, 2 = Tuesday, etc.

