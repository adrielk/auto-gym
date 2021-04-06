# auto-gym 🏋️

Auto-Gym is an automated gym reservation scheduling program that uses the [Selenium Webdriver](https://selenium-python.readthedocs.io/installation.html) for the [AFC weight room](https://www.go.recsports.virginia.edu/Program/GetProducts?classification=cc3e1e17-d2e4-4bdc-b66e-7c61999a91bf) at the University of Virginia. Since the start of the COVID school year, there is a strict capacity limit on how many people can be in the AFC weight room at once. Spots fill up quickly and it can be easy to forget when to schedule a time. This program can be run once and take care of weight room reservations for you by automatically detecting when spots open up and reserving your spot!

## How to Run

To run this program, you need to install [ChromeDriver](https://chromedriver.chromium.org/). Place the chromedriver executable in the same directory as this program. If running on Raspberry Pi, follow this [ChromeDriver installation guide](https://ivanderevianko.com/2020/01/selenium-chromedriver-for-raspberrypi) 

You also need selenium. Install these using:

`pip install -r requirements.txt`

First, make a new folder in this directory named `accounts` by entering

`mkdir accounts`

Create a text file (filename does not matter) in `accounts/` with your account information and desired reservation days and start times. Days should be formatted as a string where `1` represents Monday. An example is shown below.

```
<computing id>
<password>
12:00PM 135
3:30PM 27
5:00PM 6
```

This example tells the script to reserve start times on Monday, Wednesday, and Friday at 12:00 PM, Tuesday and Sunday at 3:30 PM, and Saturday at 5:00 PM.

To run the script, use the following command:

`python auto_gym.py <account.txt>`

If you have multiple installations of Python installed on your machine, instead run:

`python3 auto_gym.py <account.txt>`

## Running with Linux screen:

[Linux screen](https://www.howtoforge.com/linux_screen) enables you to run this script on a raspberry pi without having to keep the ssh session open. in other words, linux screen lets you close the command line interface without stopping the script. 
