from pynput import mouse
import pyautogui
from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from time import sleep, time
from threading import Thread

clickPositions = []
screenshotFolder = 'screenshots'
os.makedirs(screenshotFolder, exist_ok=True)

#Function to handle mouse click events
def onClick(x, y, button, pressed):
    if pressed:
        clickPositions.append((x, y))

#Function to capture screenshot
def captureScreenshots():
    while True:
        screenshot = pyautogui.screenshot()
        timestamp = int(time())
        screenshot.save(os.path.join(screenshotFolder, f'screenshot_{timestamp}.png'))
        sleep(10) #600 is 10 min

#Function to average all saved screenshots
def averageScreenshots():
    screenshots = [Image.open(os.path.join(screenshotFolder, f)) for f in os.listdir(screenshotFolder) if f.endswith('.png')]
    if not screenshots:
        return
    arr = np.array([np.array(im) for im in screenshots])
    avgArr = np.mean(arr, axis=0).astype(np.uint8)
    avgImage = Image.fromarray(avgArr)
    avgImage.save('averageScreenshot.png')

#Function to create a heat map from click positions
def createHeatmap():
    if not clickPositions:
        return
    x, y = zip(*clickPositions)
    
    #Capture the current screen size
    screenWidth, screenHeight = pyautogui.size()
    
    #Create a blank image with the same size as the screen
    heatmap = np.zeros((screenHeight, screenWidth))
    
    #Add circular heat spots for each click position
    for xi, yi in zip(x, y):
        heatmap[yi, xi] += 1

    #Smooth the heatmap using a Gaussian filter
    from scipy.ndimage import gaussian_filter
    heatmap = gaussian_filter(heatmap, sigma=20)
    
    #Create a colormap
    cmap = LinearSegmentedColormap.from_list("mycmap", ["blue", "cyan", "green", "yellow", "red"])

    #Plot the heatmap
    plt.clf()
    plt.imshow(heatmap, cmap=cmap, alpha=0.75, extent=(0, screenWidth, screenHeight, 0))

    #Capture the current screen for the background
    background = pyautogui.screenshot()
    background = np.array(background)
    plt.imshow(background, extent=(0, screenWidth, screenHeight, 0), alpha=0.5)
    
    plt.colorbar()
    plt.savefig('clickHeatmap.png')
    plt.show()

#Start the mouse listener
listener = mouse.Listener(on_click=onClick)
listener.start()

#Start the screenshot capturer
screenshotThread = Thread(target=captureScreenshots)
screenshotThread.start()

try:
    while True:
        userInput = input("Type 'avg' to average screenshots, 'heatmap' to generate heatmap, or 'exit' to quit: ")
        if userInput.lower() == 'avg':
            averageScreenshots()
            print("Averaged screenshot saved as 'averageScreenshot.png'.")
        elif userInput.lower() == 'heatmap':
            createHeatmap()
            print("Heatmap saved as 'clickHeatmap.png'.")
        elif userInput.lower() == 'exit':
            break
except KeyboardInterrupt:
    pass

listener.stop()
