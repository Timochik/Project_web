import os
from cloudinary.uploader import upload
import cloudinary

from dotenv import load_dotenv
load_dotenv()

def crop_image(image_url, width, height):
  """Crops an image on Cloudinary and returns the URL of the cropped version.

  Args:
      image_url (str): URL of the image on Cloudinary.
      width (int): Width of the cropped image.
      height (int): Height of the cropped image.

  Returns:
      str: URL of the cropped image.

  Raises:
      Exception: If there's an error generating the cropped URL.
  """

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Generate the transformation string for cropping
  transformation = f"c_crop,w_{width},h_{height}"

  # Construct the URL for the cropped image
  cropped_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"
  print(f"Secure URL: {cropped_url}")

  return cropped_url
  

""" image_url = "https://res.cloudinary.com/dc4ck5boh/image/upload/v1716036474/bxk0bi21q87ankm4rdw4.webp"

crop_result = crop_image(image_url, 780, 420)

if crop_result:
  print("Succesfull Crop")
else:
  print("Crop failed.") """

# Crop Secure URL: https://res.cloudinary.com/dc4ck5boh/image/upload/c_crop,w_780,h_420/bxk0bi21q87ankm4rdw4


def apply_effect(image_url, effect):
  """Applies an effect to an image on Cloudinary and returns the URL of the modified image.

  Args:
      image_url (str): URL of the image on Cloudinary.
      effect (str): Name of the effect to apply (e.g., "sepia", "vignette").
      **kwargs: Additional keyword arguments specific to the chosen effect.

  Returns:
      str: URL of the image with the applied effect.

  Raises:
      Exception: If there's an error generating the URL with the effect.
  """

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Build the transformation string for the effect
  transformation = f"e_{effect}"

  # Construct the URL for the image with effect
  effect_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"

  return effect_url

""" image_url = "https://res.cloudinary.com/dc4ck5boh/image/upload/v1716036474/bxk0bi21q87ankm4rdw4.webp"

# Apply sepia effect
sepia_url = apply_effect(image_url, "sepia")

print(f"Sepia URL: {sepia_url}") """

# Effect Sepia URL: https://res.cloudinary.com/dc4ck5boh/image/upload/e_sepia/bxk0bi21q87ankm4rdw4


def round_corners(image_url, radius):
  """Applies rounded corners to an image on Cloudinary and returns the URL of the modified image.

  Args:
      image_url (str): URL of the image on Cloudinary.
      radius (int): Radius (in pixels) of the rounded corners.

  Returns:
      str: URL of the image with rounded corners.

  Raises:
      Exception: If there's an error generating the URL with rounded corners.
  """

  # Extract public ID from the image URL (assuming the format)
  public_id = image_url.split("/")[-1].split(".")[0]

  # Build the transformation string for rounded corners
  transformation = f"r_{radius}"

  # Construct the URL for the image with rounded corners
  rounded_url = f"{image_url.split('/upload')[0]}/upload/{transformation}/{public_id}"

  return rounded_url

"""image_url = "https://res.cloudinary.com/dc4ck5boh/image/upload/v1716036474/bxk0bi21q87ankm4rdw4.webp"

# Round corners with 20px radius
rounded_url = round_corners(image_url, 90)

print(f"Rounded corners URL: {rounded_url}")

# Rounded corners url: https://res.cloudinary.com/dc4ck5boh/image/upload/r_90/bxk0bi21q87ankm4rdw4"""