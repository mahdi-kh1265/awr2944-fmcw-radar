import cv2
import numpy as np

img = cv2.imread(r'C:\Users\khams008\.gemini\antigravity-ide\brain\c904b166-8a91-4f95-8f9c-75156c56e83b\media__1783715270715.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# In MATLAB desktop (classic), axes are typically white (255) boxes inside a grey (240) figure.
# Let's find large white rectangles which are the axes interiors.
_, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

rects = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w > 100 and h > 100: # large enough to be an axes
        rects.append((x, y, w, h))

# Sort by y then x
rects = sorted(rects, key=lambda r: (r[1], r[0]))
for i, r in enumerate(rects):
    # MATLAB position uses origin at bottom-left!
    # image height is 583. So bottom = 583 - y - h
    matlab_y = 583 - r[1] - r[3]
    print(f"Axes {i}: [x={r[0]}, y_img={r[1]}, w={r[2]}, h={r[3]}] -> MATLAB: [{r[0]}, {matlab_y}, {r[2]}, {r[3]}]")

# Let's also find the parameter table (often white inside grey)
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w > 200 and h > 200 and x > 800: # Table is on the right
        matlab_y = 583 - y - h
        print(f"Table candidate: MATLAB: [{x}, {matlab_y}, {w}, {h}]")

