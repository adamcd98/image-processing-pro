import cv2
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import math
import time
# import keyboard as kyb
# import vgamepad as vg
from pynput.keyboard import Controller, Key  # Use pynput instead of keyboard

keyboard = Controller()


# Create a virtual gamepad object
# gamepad = vg.VX360Gamepad()


# ------------------------------------- functions -------------------------------------#

class MovementStateMachine:
    def __init__(self, cooldown_time=0.5):
        self.state_p1 = "idle"
        self.state_p2 = "idle"
        self.last_movement_time_p1 = 0
        self.last_movement_time_p2 = 0
        self.cooldown_time = cooldown_time  # Cooldown in seconds

    def detect_movement(self, center_of_mass, roi_center, player):
        current_time = time.time()

        # Select player-specific variables
        if player == "P1":
            last_time = self.last_movement_time_p1
            state = self.state_p1
        else:
            last_time = self.last_movement_time_p2
            state = self.state_p2

        # Apply cooldown
        if current_time - last_time < self.cooldown_time:
            return "idle"

        dx, dy = center_of_mass[0] - roi_center[0], center_of_mass[1] - roi_center[1]

        # If movement is too small, stay in 'idle'
        if np.linalg.norm([dx, dy]) < 100:
            return "idle"

        angle = math.atan2(dy, dx)
        new_state = "idle"
        key_to_press = None

        # Determine movement direction
        if -0.2 * math.pi <= angle < 0.2 * math.pi:
            new_state = "left"
            key_to_press = Key.left if player == "P1" else "a"
        elif dy > 50:
            new_state = "down"
            key_to_press = Key.down if player == "P1" else "s"
        elif -0.8 * math.pi <= angle < -0.2 * math.pi:
            new_state = "up"
            key_to_press = Key.up if player == "P1" else "w"
        else:
            new_state = "right"
            key_to_press = Key.right if player == "P1" else "d"

        # Trigger key press if new state differs from the last one
        if state != new_state and key_to_press:
            if player == "P1":
                self.state_p1 = new_state
                self.last_movement_time_p1 = current_time
            else:
                self.state_p2 = new_state
                self.last_movement_time_p2 = current_time

            print(f"{player} Movement: {new_state}")

            keyboard.press(key_to_press)
            time.sleep(0.01)  # Short delay for key press
            keyboard.release(key_to_press)
            time.sleep(self.cooldown_time)
            return new_state

        return "idle"


class MovementStateMachine_rectangles:
    def __init__(self, cooldown_time=0.5):
        self.state_p1 = "idle"
        # self.frame_tresh=frame_tresh
        self.state_p2 = "idle"
        self.last_movement_time_p1 = 0
        self.last_movement_time_p2 = 0
        self.cooldown_time = cooldown_time  # Cooldown in seconds

    def detect_movement(self, mask, min_area, regions, player, down=False):
        current_time = time.time()

        # Select player-specific variables
        if player == "P1":
            last_time = self.last_movement_time_p1
            state = self.state_p1
        # frame_count=self.frame_count_p1
        else:
            last_time = self.last_movement_time_p2
            # frame_count=self.frame_count_p2
            state = self.state_p2

        # Apply cooldown
        if current_time - last_time < self.cooldown_time:
            return "idle"

        # Define regions
        left_rect, right_rect, up_rect = regions  # (x,y,w,h) x 4

        # Calculate detected area inside each region
        left_area = count_pixels_inside_rectangle(mask, left_rect)
        right_area = count_pixels_inside_rectangle(mask, right_rect)
        up_area = count_pixels_inside_rectangle(mask, up_rect)

        max_area = max(left_area, right_area, up_area)

        # if the detected area too small, stay in "idle"
        if max_area < min_area and down == False:
            if player == "P1":
                self.state_p1 = "idle"
            else:
                self.state_p2 = "idle"
            return "idle"

        new_state = "idle"
        key_to_press = None
        #  if player == "P1":
        #     print(f"player 1{down}")
        # else:
        #     print(f"player 2{down}")

        # Determine movement direction
        if max_area == left_area:
            new_state = "left"
            key_to_press = Key.left if player == "P1" else "a"
        elif max_area == up_area:
            new_state = "up"
            key_to_press = Key.up if player == "P1" else "w"
        else:
            new_state = "right"
            key_to_press = Key.right if player == "P1" else "d"

        if down:
            new_state = "down"
            key_to_press = Key.down if player == "P1" else "s"
            down = False

        # Trigger key press if new state differs from the last one
        if state != new_state and key_to_press:
            if player == "P1":
                self.state_p1 = new_state
                self.last_movement_time_p1 = current_time
            else:
                self.state_p2 = new_state
                self.last_movement_time_p2 = current_time

            print(f"{player} Movement: {new_state}")
            if player == "P1":
                keyboard.press(key_to_press)
                time.sleep(0.01)  # Short delay for key press
                keyboard.release(key_to_press)
            else:
                '''
                if key_to_press == "w":
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                    gamepad.update()

                # Check if the 's' key is pressed
                if key_to_press == "s":  # DOWN on D-pad
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                    gamepad.update()

                # Check if the 'a' key is pressed
                if key_to_press == "a":  # LEFT on D-pad
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                    gamepad.update()

                # Check if the 'd' key is pressed
                if key_to_press == "d":  # RIGHT on D-pad
                    gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                    gamepad.update()

                time.sleep(0.01)
                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
                gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                gamepad.update()
                '''
            return new_state

        return "idle"


def count_pixels_inside_rectangle(mask, region):
    """Counts nonzero pixels inside a given rectangle in a binary mask."""
    x, y, w, h = region
    roi = mask[y:y + h, x:x + w]  # Extract the ROI from the mask
    return np.count_nonzero(roi)  # Count nonzero (white) pixels


def skin_segmentation(image):
    hist = get_hs_histogram(image, None)
    data = extract_histogram_data(hist)
    clustering = AgglomerativeClustering(distance_threshold=1000, n_clusters=None)
    labels = clustering.fit_predict(data)
    classified_hist = create_classified_histogram(hist, data, labels)
    classified_img = create_classified_image(image, classified_hist)
    circle_mask = np.zeros((w1L, w1L))
    circle_mask = cv2.circle(circle_mask, (w1L // 2, w1L // 2), w1L // 4, 255, -1)
    skin_mask = create_mask_from_top_k_labels_given_mask(classified_img, circle_mask, 1)
    skin_segment = cv2.bitwise_and(image, image, mask=skin_mask)
    return skin_mask, skin_segment


def filter_large_and_far_contours(skin_mask, min_area=1000, max_dist=100):
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros_like(skin_mask), []
    largest_contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]
    large_contours = []
    filtered_mask = np.zeros_like(skin_mask)
    for contour in contours:
        if cv2.contourArea(contour) > min_area and distance(contour, largest_contour) < max_dist:
            cv2.drawContours(filtered_mask, [contour], -1, 255, thickness=cv2.FILLED)
            large_contours.append(contour)
    return filtered_mask, large_contours


def filter_head(skin_mask, center, radius):
    # Create a black (all zeros) image with the same size as the skin_mask
    circle_mask = np.zeros_like(skin_mask, dtype=np.uint8)

    # Draw a white (255) filled circle in the circle_mask at the specified center with the specified radius
    cv2.circle(circle_mask, center, radius, (255), thickness=cv2.FILLED)

    # Use bitwise AND with the inverse of the circle mask to keep everything except the circle area
    skin_mask_removed = cv2.bitwise_and(skin_mask, cv2.bitwise_not(circle_mask))

    return skin_mask_removed


def calculate_center_of_mass(mask):
    """
    Calculates the center of mass (weighted centroid) of the masked region.
    """
    moments = cv2.moments(mask)
    if moments["m00"] == 0:
        return None  # No mass (i.e., no skin area detected)
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])
    return cx, cy


def centroid(contour):
    M = cv2.moments(contour)
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])


def distance(contour1, contour2):
    centroid1, centroid2 = centroid(contour1), centroid(contour2)
    return np.sqrt((centroid1[0] - centroid2[0]) ** 2 + (centroid1[1] - centroid2[1]) ** 2)


def get_hs_histogram(hand_img, mask):
    """Computes the HSV histogram of a given masked image."""
    hsv_hand = cv2.cvtColor(hand_img, cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist([hsv_hand], [0, 1], mask, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    return hist


def apply_backprojection(target_img, ref_hist, thresh=50):
    """
        Applies histogram backprojection to find regions in target_img matching the reference histogram.
        z
        """
    hsv_target = cv2.cvtColor(target_img, cv2.COLOR_BGR2HSV)

    # Compute the backprojection
    back_proj = cv2.calcBackProject([hsv_target], [0, 1], ref_hist, [0, 180, 0, 256], scale=1)

    # Apply a convolution to smooth the image
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    back_proj = cv2.filter2D(back_proj, -1, disc)

    # Threshold and apply morphology to clean up noise
    _, thresholded = cv2.threshold(back_proj, thresh, 255, cv2.THRESH_BINARY)
    thresholded = np.uint8(thresholded)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    cleaned = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    return cleaned, back_proj


def extract_hands_hist(roi_img1, roi_img2):
    skin_mask1, _ = skin_segmentation(roi_img1)
    skin_mask2, _ = skin_segmentation(roi_img2)
    filtered_mask1, _ = filter_large_and_far_contours(skin_mask1)
    filtered_mask2, _ = filter_large_and_far_contours(skin_mask2)
    masked_image1 = cv2.bitwise_and(roi_img1, roi_img1, mask=filtered_mask1)
    masked_image2 = cv2.bitwise_and(roi_img2, roi_img2, mask=filtered_mask2)

    ref_hist1 = get_hs_histogram(masked_image1, filtered_mask1)
    ref_hist2 = get_hs_histogram(masked_image2, filtered_mask2)

    ref_hist = (ref_hist1 + ref_hist2) / 2
    cv2.normalize(ref_hist, ref_hist, 0, 255, cv2.NORM_MINMAX)
    return ref_hist


def mask_corners(roi, size=0.1):
    _, _, w, h = roi
    mask = np.ones((h, w), dtype=np.uint8)
    corner_size = int(min(w, h) * size)
    mask[:corner_size, :] = 0
    mask[-corner_size:, :] = 0
    mask[:, :corner_size] = 0
    mask[:, -corner_size:] = 0
    return mask


def find_object_centroids(mask, k=3):
    # Find all nonzero points in the mask
    points = np.column_stack(np.where(mask > 0))

    if len(points) < k:
        raise ValueError("Not enough points to form the required clusters")

    # Convert points to float32 for k-means
    points = np.float32(points)

    # Define criteria for k-means (stop after 10 iterations or when movement is < 1.0)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    # Apply k-means clustering
    _, labels, centers = cv2.kmeans(points, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

    return np.int32(centers)  # Convert centers back to integer coordinates


def draw_rect(frame, rect, color="blue"):
    x, y, w, h = rect
    if color == "blue":
        color_bgr = (255, 0, 0)
    elif color == "green":
        color_bgr = (0, 255, 0)
    elif color == "red":
        color_bgr = (0, 0, 255)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, 2)  # 2 is the thickness of the rectangle
    return


def extract_histogram_data(hist):
    """Extracts (Hue, Saturation) values without considering frequency."""
    h_bins, s_bins = hist.shape
    data = []
    flag = 0
    for h in range(h_bins):
        for s in range(s_bins):
            freq = hist[h, s]
            if freq > 0:  # Only add non-zero bins
                for f in range(int(freq)):
                    data.append([h, s])

    return np.array(data)


def create_classified_histogram(hist, data, labels):
    """Creates a classified 2D histogram array with cluster labels."""
    classified_hist = np.zeros_like(hist)  # Create an array with the same shape as the histogram

    for i, label in enumerate(labels):
        h, s = data[i]
        classified_hist[h, s] = label

    return classified_hist


def create_classified_image(roi_img, classified_hist):
    """Creates a classified image from the clustering labels efficiently."""
    hsv_img = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
    H = roi_img.shape[0]
    W = roi_img.shape[1]
    classified_img = np.zeros((H, W), dtype=np.uint8)
    for i in range(H):
        for j in range(W):
            h, s = hsv_img[i, j][:2]
            classified_img[i, j] = classified_hist[h, s]
    return classified_img


def create_mask_from_top_k_labels_given_mask(classified_img, circle_mask, k):
    # Extract labels within the circular mask
    labels_in_circle = classified_img[circle_mask == 255]

    # Count frequency of each label
    unique, counts = np.unique(labels_in_circle, return_counts=True)
    label_counts = dict(zip(unique, counts))

    # Select the k most frequent labels
    top_k_labels = sorted(label_counts, key=label_counts.get, reverse=True)[:k]

    # Create the final mask: 255 where labels belong to the top-k, 0 otherwise
    final_mask = np.isin(classified_img, top_k_labels).astype(np.uint8) * 255

    # Apply morphological operations to clean the mask:
    kernel = np.ones((5, 5), np.uint8)  # You can adjust the kernel size for more or less effect

    # Noise removal (Opening: Erosion followed by Dilation)
    cleaned_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)

    # Gap filling (Closing: Dilation followed by Erosion)
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel)

    return cleaned_mask


def avoid_shrinking(window):
    x, y, w, h = window
    xmax = width // 2
    x = max(int(0.2 * xmax), min(x, int(0.8 * xmax) - w))
    y = max(int(0.2 * height), min(y, height - h))
    new_window = (x, y, w, h)
    return new_window


def reinit_window(window, frame):
    x, y, w, h = window
    min_area = (w * h) / 8
    area = count_pixels_inside_rectangle(frame, window)
    if area < min_area:
        xmin, xmax = int(0.2 * width // 2), int(0.8 * width // 2 - w)
        narrow_frame = frame[:, xmin:xmax]
        center_of_mass = calculate_center_of_mass(narrow_frame)
        if center_of_mass is not None:
            cx, cy = center_of_mass
            cx += xmin
            x, y, w, h = window
            return cx, cy, w, h
    return window


def head_down(window, thresh, scaling_thresh=0.35):
    # print(f'scaling_thresh * thresh{scaling_thresh * thresh}')
    _, y_head, _, _ = window
    # print(f'y_head{y_head}')
    if y_head > scaling_thresh * thresh:
        return True
    return False


# ------------------------------------- calibration -------------------------------------#

cap = cv2.VideoCapture(0)  # Change this if using an external camera (e.g., cap = cv2.VideoCapture(1))
# Set resolution (increase the frame size)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set width (e.g., 1920 for Full HD)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Set height (e.g., 1080 for Full HD)
# Display ROIs for 5 seconds for hand calibration
start_time = time.time()
while time.time() - start_time < 7:
    ret, frame = cap.read()
    if not ret:
        break
    remaining_time = int(7 - (time.time() - start_time))
    # Get frame's dimentions
    h = frame.shape[0]
    w = frame.shape[1]

    # Define rois
    roi_1_left = (w // 20, h // 3, w // 12, w // 12)
    roi_1_right = (7 * w // 20, h // 3, w // 12, w // 12)
    roi_head_1 = (18 * w // 100, h // 5, w // 10, w // 10)

    roi_2_left = (17 * w // 20, h // 3, w // 12, w // 12)
    roi_2_right = (11 * w // 20, h // 3, w // 12, w // 12)
    roi_head_2 = (27 * w // 40, h // 5, w // 10, w // 10)

    # Draw rectangles for both players' hands
    for (x, y, w, h) in [roi_1_left, roi_1_right, roi_2_left, roi_2_right]:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (x + w // 2, y + w // 2), w // 4, 255, 3)

    # Draw rectangles for both players' heads
    for (x, y, w, h) in [roi_head_1, roi_head_2]:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    flipped_frame = cv2.flip(frame, 1)
    cv2.putText(flipped_frame, f"Place your hands in the boxes! time remaining :{remaining_time}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    height, width, _ = frame.shape
    split_x = width // 2  # Split screen into two halves

    cv2.line(flipped_frame, (split_x, 0), (split_x, height), (0, 255, 0), 2)
    cv2.imshow("Setup", flipped_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Capture reference image
ret, ref_image = cap.read()
cv2.imwrite('reference_image.png', ref_image)
if not ret:
    print("Failed to capture reference image")
    cap.release()
    cv2.destroyAllWindows()
    exit()

print("Hand detection setup complete!")

cv2.destroyAllWindows()

# ------------------------------------- data extraction from ref -------------------------------------#
# Extract ROIs from reference image for each hand
x1L, y1L, w1L, h1L = roi_1_left
x1R, y1R, w1R, h1R = roi_1_right
x2L, y2L, w2L, h2L = roi_2_left
x2R, y2R, w2R, h2R = roi_2_right

roi_img1L = ref_image[y1L:y1L + h1L, x1L:x1L + w1L]  # Player 1 Left Hand
roi_img1R = ref_image[y1R:y1R + h1R, x1R:x1R + w1R]  # Player 1 Right Hand
roi_img2L = ref_image[y2L:y2L + h2L, x2L:x2L + w2L]  # Player 2 Left Hand
roi_img2R = ref_image[y2R:y2R + h2R, x2R:x2R + w2R]  # Player 2 Right Hand

# Extract histograms for each hand separately
ref_hist1 = extract_hands_hist(roi_img1L, roi_img1R)  # Player 1 Left Hand
ref_hist2 = extract_hands_hist(roi_img2L, roi_img2R)  # Player 2 Left Hand

print('hand histogram calculated')

hand_area_1 = 100
hand_area_2 = 100

# Initialize movement state machine
movement_machine = MovementStateMachine_rectangles(cooldown_time=0.5)  # Set cooldown to 0.5s

offset = 0  # Adjust this value to move the ROI center further down

# Define decision regions (x,y,w,h)
h = ref_image.shape[0]
w = ref_image.shape[1] // 2
left_rect = (w - 2 * w // 10, w // 6, w // 10, h // 6)
right_rect = (w // 20, w // 6, w // 10, h // 6)
up_rect = (3 * w // 10, 0, 3 * w // 10, h // 6)

decision_regions_1 = np.array([left_rect, right_rect, up_rect])
decision_regions_2 = decision_regions_1 + np.array([w, 0, 0, 0])

decision_regions_1 = tuple(decision_regions_1.tolist())
decision_regions_2 = tuple(decision_regions_2.tolist())

# Windows for tracking

left_window_1, right_window_1 = roi_1_left, roi_1_right
shift = np.array([-w, 0, 0, 0])
left_window_2, right_window_2 = tuple(np.array(roi_2_left) + shift), tuple(np.array(roi_2_right) + shift)
tracked_windows = [left_window_1, right_window_1, left_window_2, right_window_2]

head_window_1 = roi_head_1
head_window_2 = tuple(np.array(roi_head_2) + shift)
heads_windows = [head_window_1, head_window_2]

# ------------------------------------- live -------------------------------------#
movement_history_p1 = []
movement_history_p2 = []
frame_threshold = 10  # Number of consecutive frames to confirm a movement

# Start processing live frames for movement detection
while True:
    ret, scene = cap.read()
    if not ret:
        break

    height, width, _ = scene.shape
    split_x = width // 2  # Split screen into two halves

    scene1 = scene[:, :split_x]  # Player 1 area
    scene2 = scene[:, split_x:]  # Player 2 area

    # Convert to grayscale
    gray_scene_1 = cv2.cvtColor(scene1, cv2.COLOR_BGR2GRAY)
    gray_scene_2 = cv2.cvtColor(scene2, cv2.COLOR_BGR2GRAY)

    # Apply backprojection using respective histograms
    skin_mask1, back_proj_1 = apply_backprojection(scene1, ref_hist1, thresh=20)  # Player 1
    skin_mask2, back_proj_2 = apply_backprojection(scene2, ref_hist2, thresh=20)  # Player 2

    # Filter out noise
    filtered_mask1, _ = filter_large_and_far_contours(skin_mask1, min_area=4000, max_dist=1000)
    filtered_mask2, _ = filter_large_and_far_contours(skin_mask2, min_area=4000, max_dist=1000)

    # Apply mask to grayscale images
    masked_scene1 = cv2.bitwise_and(gray_scene_1, gray_scene_1, mask=filtered_mask1)
    masked_scene2 = cv2.bitwise_and(gray_scene_2, gray_scene_2, mask=filtered_mask2)

    # Apply mask to probability img
    masked_backproj_1 = cv2.bitwise_and(back_proj_1, back_proj_1, mask=filtered_mask1)
    masked_backproj_2 = cv2.bitwise_and(back_proj_2, back_proj_2, mask=filtered_mask2)

    # Convert grayscale back to color for visualization
    frame_with_mask1 = cv2.cvtColor(masked_backproj_1, cv2.COLOR_GRAY2BGR)
    frame_with_mask2 = cv2.cvtColor(masked_backproj_2, cv2.COLOR_GRAY2BGR)

    # Apply Heads Meanshift
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
    for i, window in enumerate(heads_windows):
        if i == 0:  # P1
            _, new_window = cv2.meanShift(masked_backproj_1, window, term_crit)
            new_window = avoid_shrinking(new_window)
            new_window = reinit_window(new_window, masked_backproj_1)
            draw_rect(frame_with_mask1, new_window, "red")
            heads_windows[i] = new_window
        else:  # P2
            _, new_window = cv2.meanShift(masked_backproj_2, window, term_crit)
            new_window = avoid_shrinking(new_window)
            new_window = reinit_window(new_window, masked_backproj_2)
            draw_rect(frame_with_mask2, new_window, "blue")
            heads_windows[i] = new_window

    head_1, head_2 = heads_windows[0], heads_windows[1]
    down_1, down_2 = head_down(head_1, height), head_down(head_2, height)

    '''
    LONG_PRESS_TIME = 5.0  # Second press should be held for 5 seconds
    if kyb.is_pressed('f'):
        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(0.1)  # Short press duration
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
    if kyb.is_pressed('h'):  # Second press should be long
        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()
        time.sleep(LONG_PRESS_TIME)  # Hold for 5 seconds
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.update()

    '''
    # Detect movement
    movement1 = movement_machine.detect_movement(filtered_mask1, hand_area_1 / 2, decision_regions_1, "P2", down=down_1)
    movement2 = movement_machine.detect_movement(filtered_mask2, hand_area_2 / 2, decision_regions_1, "P1",
                                                 down=down_2)  # keep decision regions 1!

    # Flip images for correct display orientation
    flipped_scene1 = cv2.flip(frame_with_mask1, 1)
    flipped_scene2 = cv2.flip(frame_with_mask2, 1)

    # Combine frames for display
    combined_frame = np.hstack((flipped_scene2, flipped_scene1))
    combined_real = np.hstack((scene2, scene1))

    # Draw decision rectangles
    for rect in decision_regions_1 + decision_regions_2:
        rect_x, rect_y, rect_w, rect_h = rect
        cv2.rectangle(combined_frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

    for rect in decision_regions_1 + decision_regions_2:
        rect_x, rect_y, rect_w, rect_h = rect
        cv2.rectangle(combined_real, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

    # Display movement labels
    cv2.putText(combined_frame, f"P1: {movement1}", (50, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(combined_frame, f"P2: {movement2}", (split_x + 50, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    cv2.putText(combined_real, f"P1: {movement1}", (50, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(combined_real, f"P2: {movement2}", (split_x + 50, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 0), 2)

    # Show the output frames
    cv2.imshow("Two-Player Motion Detection", combined_frame)
    cv2.imshow("Two-Player Motion no", combined_real)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()