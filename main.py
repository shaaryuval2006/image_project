
import cv2
import numpy as np
from PIL import Image



def present_res(image_path, image_path2):
    img = cv2.imread(image_path2)
    imS = cv2.resize(img, (1600, 200))
    cv2.imshow("Stitched Image", imS)
    imS = cv2.resize(img, (1600, 100))
    cv2.imshow("Stitched Image", imS)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

def stitch_images(image_paths, output_path, output_path2):
    try:
        # Read each image using OpenCV
        images = [cv2.imread(image_path + path) for path in image_list]
        # Get the height and width of the first image
        height, width, _ = images[0].shape
        window = 80
        # Calculate the total width for the stitched image
        total_width2 = window * len(images)
        total_width = width * len(images)
        # Create a new image with the total width
        stitched_image = np.zeros((height, total_width, 3), dtype=np.uint8)
        stitched_image2 = np.zeros((height, total_width2, 3), dtype=np.uint8)
        # Paste each image onto the stitched image
        for i, image in enumerate(images):
            #stitched_image[:, i * width:(i + 1) * width, :] = image
            stitched_image2[:, i * window :(i + 1) * window , :] = image[:, width // 2 - window // 2: width // 2 + window // 2, :]
        # Save the stitched image with a .png extension
        #cv2.imwrite(output_path, stitched_image, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
        cv2.imwrite(output_path2, stitched_image2, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])

        print(f"Stitched image saved successfully to {output_path}")

        # Display the stitched image
        #cv2.imshow("Stitched Image", stitched_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
image_list = ["new_image1.jpeg", "new_image2.jpeg", "new_image3.jpeg", "new_image4.jpeg", "new_image5.jpeg",
               "new_image6.jpeg", "new_image7.jpeg", "new_image8.jpeg", "new_image9.jpeg", "new_image10.jpeg" , "new_image11.jpeg"
                ,"new_image12.jpeg", "new_image13.jpeg" , "new_image14.jpeg" , "new_image15.jpeg" , "new_image16.jpeg" , "new_image17.jpeg" , "new_image18.jpeg" , "new_image19.jpeg" , "new_image20.jpeg"]
output_path = "stitched_image_without_pillow.png"
output_path2 = "stitched_image_without_pillow2.png"
image_path = "new_images\\"
stitch_images(image_list, output_path, output_path2)

present_res(output_path, output_path2)
print("a")