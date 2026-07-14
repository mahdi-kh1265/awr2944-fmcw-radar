import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os

ref_path = r'C:\Users\khams008\.gemini\antigravity-ide\brain\c904b166-8a91-4f95-8f9c-75156c56e83b\mmws_reference_1151x582.png'
gen_path = r'C:\Users\khams008\Documents\awr2944-fmcw-radar\matlab\viewer\mockup_getframe.png'
out_dir = r'C:\Users\khams008\.gemini\antigravity-ide\brain\c904b166-8a91-4f95-8f9c-75156c56e83b'

ref_img = cv2.imread(ref_path)
gen_img = cv2.imread(gen_path)

# The user expects 1151x582
target_shape = (1151, 582) # width, height for cv2.resize
if ref_img.shape[1] != 1151 or ref_img.shape[0] != 582:
    ref_img = cv2.resize(ref_img, target_shape)

if gen_img.shape[1] != 1151 or gen_img.shape[0] != 582:
    gen_img = cv2.resize(gen_img, target_shape)

ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
gen_gray = cv2.cvtColor(gen_img, cv2.COLOR_BGR2GRAY)

# Calculate full SSIM
score_full, diff = ssim(ref_gray, gen_gray, full=True)
print(f"Full-Window SSIM Score: {score_full:.4f}")

# Mask out plot interiors to compute "shell-only" SSIM
mask = np.ones_like(ref_gray)
boxes = [
    (57, 38, 344, 229), # topLeft
    (448, 38, 344, 229), # topRight
    (57, 324, 344, 229), # bottomLeft
    (448, 324, 344, 229) # bottomMiddle
]
for (x, y, w, h) in boxes:
    mask[y:y+h, x:x+w] = 0

score_shell, _ = ssim(ref_gray * mask, gen_gray * mask, full=True)
print(f"Shell-Only SSIM Score: {score_shell:.4f}")

# Heatmap
abs_diff = cv2.absdiff(ref_img, gen_img)
_, thresh = cv2.threshold(cv2.cvtColor(abs_diff, cv2.COLOR_BGR2GRAY), 30, 255, cv2.THRESH_BINARY)
diff_heatmap = cv2.applyColorMap(cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR), cv2.COLORMAP_JET)

side_by_side = np.hstack((ref_img, gen_img))
overlay = cv2.addWeighted(ref_img, 0.5, gen_img, 0.5, 0)

# Geometry/Edge overlay
edges_ref = cv2.Canny(ref_gray, 50, 150)
edges_gen = cv2.Canny(gen_gray, 50, 150)

# Red for ref edges, Green for gen edges
edge_overlay = np.zeros_like(ref_img)
edge_overlay[edges_ref > 0] = [0, 0, 255] # BGR
edge_overlay[edges_gen > 0] = np.maximum(edge_overlay[edges_gen > 0], [0, 255, 0])

cv2.imwrite(os.path.join(out_dir, 'pixel_diff.png'), diff_heatmap)
cv2.imwrite(os.path.join(out_dir, 'side_by_side.png'), side_by_side)
cv2.imwrite(os.path.join(out_dir, 'overlay.png'), overlay)
cv2.imwrite(os.path.join(out_dir, 'edge_overlay.png'), edge_overlay)
