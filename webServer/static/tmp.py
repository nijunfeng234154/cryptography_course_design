import io
import base64
from PIL import Image

# Read the file content
with open("./saveBase64", "r") as f:
    base64_image = f.read().encode("utf-8")

# Decode the BASE64 string to bytes
# image_bytes = base64.b64decode(base64_image)

# Open the image
# p = Image.open(io.BytesIO(image_bytes))
pp = Image.open("./gary.jpg")
pp_b = base64.b64encode(pp.tobytes())
print(pp_b == base64_image)
with open("./saveBase64-2", "w") as f:
    f.write(pp_b.decode("utf8"))


