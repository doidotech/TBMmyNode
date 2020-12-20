#-------------------------------------------------------------------------------
#   Copyright (c) 2020 DOIDO Technologies
#
#   Author   : Walter
#   Version  : 2.0.4
#   Location : github
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This script displays two screens for the Mynode project:
#    1. First screen displays the Mynode boot screen.
#    2. Second screen has bitcoin price and current bitcoin block.
#    3. First screen is displayed during boot, for 45 seconds.
#    4. Second screen is displayed indefinitely.   
#-------------------------------------------------------------------------------

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

import urllib.request as urlreq
import certifi
import ssl
import json
import socket
import pathlib
import subprocess

WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000


# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display.
disp.begin()


# Clear display, white background
disp.clear((255, 255, 255))
disp.display()

# Get a PIL Draw object to start drawing on the display buffer.
draw = disp.draw()

#Get directory of the executing script
filePath=str(pathlib.Path(__file__).parent.absolute())

# customizable images path
images_path = filePath+'/images/'

# Customizable fonts path
caviar_dreams_fonts_path = filePath+'/caviar_dreams/'
helveticaneue_fonts_path = filePath+'/helveticaneue/'
galyon_fonts_path = filePath+'/galyon/'

# Define a function to calculate an inverted x co-ordinate.
def get_inverted_x(currentX, objectSize):
    invertedX = WIDTH - (currentX + objectSize)
    return invertedX
    
# Define a function to draw the lcd background image.
def display_background_image(image_name):
    # Load an image.
    image_path = images_path+image_name
    image = disp.buffer
    position = (0,0)
    picimage = Image.open(image_path)
    # Convert to RGBA
    picimage = picimage.convert('RGBA')
    # Resize the image
    picimage = picimage.resize((160, 128), Image.BICUBIC)
    # Rotate image
    rotated = picimage.rotate(270, expand=1)
    # Paste the image into the screen buffer
    image.paste(rotated, position, rotated)
    
# Define a function to draw an icon.
def display_icon(image, image_path, position,icon_size):
    # Load an image.
    picimage = Image.open(image_path)
    # Convert to RGBA
    picimage = picimage.convert('RGBA')
    # Resize the image
    picimage = picimage.resize((icon_size, icon_size), Image.BICUBIC)
    # Rotate image
    rotated = picimage.rotate(270, expand=1)
    # Paste the image into the screen buffer
    image.paste(rotated, position, rotated)
    
# Define a function to display orange line image.
def display_orange_line(image, image_path, position):
    # Load an image.
    picimage = Image.open(image_path)
    # Convert to RGBA
    picimage = picimage.convert('RGBA')
    # Resize the image
    y_size = 4
    x_size = 135
    picimage = picimage.resize((x_size, y_size), Image.BICUBIC)
    # Rotate image
    rotated = picimage.rotate(270, expand=1)
    # Paste the image into the screen buffer
    image.paste(rotated, position, rotated)
    
# Define a function to create left justified text.
def draw_left_justified_text(image, text, xposition, yPosition, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    W, H = (128,160)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    xCordinate = xposition
    #yCordinate = int((H-width)-yPosition)
    yCordinate = yPosition
    
    image.paste(rotated, (xCordinate,yCordinate), rotated)
    
# Define a function to create right justified text.
def draw_right_justified_text(image, text, xposition, yPosition, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    W, H = (128,160)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    xCordinate = xposition
    yCordinate = int((H-width)-yPosition)
    #yCordinate = yPosition
    
    image.paste(rotated, (xCordinate,yCordinate), rotated)
    
# Define a function to display temperature
def display_temperature(screenType):
    # Measure temperature
    temp_result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    temp_string = temp_result.stdout.decode('utf-8')
    raw_temp = temp_string.replace("temp=","")
    raw_temp = raw_temp.replace("'C","")
    raw_temp = raw_temp.strip()
    raw_temp_float = float(raw_temp)
    raw_temp = str(int(raw_temp_float))
    #print('Raw temp: '+raw_temp)
    temperature = raw_temp.strip()
    # display temperature
    temp_font = ImageFont.truetype(caviar_dreams_fonts_path+"CaviarDreams_Bold.ttf", 18)
    draw_right_justified_text(disp.buffer, "°", 10,10, 270, temp_font, fill="#BF1553")
    # Seperate colors for the screens
    if screenType == 1:
        draw_right_justified_text(disp.buffer, temperature, 10,17, 270, temp_font, fill="#4E6D7A")
    else:
        draw_right_justified_text(disp.buffer, temperature, 10,17, 270, temp_font, fill="#595959")

# Define a function to return a comma seperated number
def place_value(number): 
    return ("{:,}".format(number))

# Define a function to get current block height in the longest chain
def get_block_count():
    try:
        url = "https://blockchain.info/q/getblockcount"
        currentBlock = urlreq.urlopen(url, context=ssl.create_default_context(cafile=certifi.where())).read()
        currentBlockString = currentBlock.decode('utf-8')
        #print("Current block: " + currentBlockString)
        return place_value(int(currentBlockString))
    except:
        print("Error while getting current block")
        return ""
    
# Define a function get bitcoin price
def get_btc_price():
    try:
        url = "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=KES,USD"
        currentPrice = urlreq.urlopen(url, context=ssl.create_default_context(cafile=certifi.where())).read()
        price_dict = json.loads(currentPrice)
        price = int(price_dict['USD'])
        #price='99,999'
        #print("$" + price)
        return place_value(price)
    except:
        print("Error while getting price")
        return ""
    
# Define a function to draw current Bitcoin price and block screen
def draw_btc_price_and_block():
    # Display background first
    display_background_image('Screen1@288x.png')
    # Display bitcoin icon
    display_icon(disp.buffer, images_path+'bitcoin.png', (get_inverted_x(16,36),10),36)
    # Display current bitcoin price
    new_price = get_btc_price()
    #new_price = '99,999'
    price_font = ImageFont.truetype(helveticaneue_fonts_path+"HelveticaNeuBold.ttf", 30)
    draw_left_justified_text(disp.buffer, new_price, get_inverted_x(14,35),52, 270, price_font, fill=(255,255,255))
    # Display umbrel icon
    block_x_pos = 75
    block_y_pos = 13
    display_icon(disp.buffer, images_path+'Block_Icon.png', (get_inverted_x(block_x_pos,30),block_y_pos),30)
    # Display current bitcoin block
    btc_current_block = get_block_count()
    #btc_current_block = '9,999,999'
    block_num_font = ImageFont.truetype(helveticaneue_fonts_path+"HelveticaNeuBold.ttf", 20)
    draw_left_justified_text(disp.buffer, btc_current_block, get_inverted_x(block_x_pos+5,20),(block_y_pos+37), 270, block_num_font, fill=(255,255,255))
    # Draw the line
    line_upper_x_pos = get_inverted_x(16,37) # bitcoin icon x pos
    line_lower_x_pos = get_inverted_x(block_x_pos,0)
    line_y_pos = 28 #(10 left margin, 18 radius of bitcoin icon)
    shape = [(line_upper_x_pos, line_y_pos), (line_lower_x_pos, line_y_pos)]
    draw.line(shape, fill ="#969994", width = 2) 
    # Display temperature
    display_temperature(1)
    
        
# Start the display of images now.
print('Running Mynode LCD script Version 2.0.4')
#Display Mynode boot screen for 45 seconds
display_background_image('Mynode_Bootscreen.png')
disp.display()
time.sleep(45)

while True:
    try:  
        # Display price and block screen for 30s
        disp.clear((255, 255, 255))
        draw_btc_price_and_block()
        disp.display()
        time.sleep(30)
    except:
        print("error")





