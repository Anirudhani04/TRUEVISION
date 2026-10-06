
import matplotlib.pyplot as plt
import gc

from mantranet import *
import shutil
from pytorch_lightning import Trainer
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from .models import ifd
from .mantranet import pre_trained_model



def checkImage(request):
  
    file = request.FILES.get('image')
    fss = FileSystemStorage()
    filename = fss.save(file.name, file)
    file_path = fss.path(filename)
    
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    import torch
    import torchvision.transforms as T
    from PIL import Image
    from model.networks_tf import Generator  # Ensure correct import for your inpainting model

    # --------- Step 1: Apply ELA (Error Level Analysis) ---------
    def apply_ela(image_path, quality=90):
        original = cv2.imread(image_path)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)

        # Save compressed version
        temp_path = "temp_compressed.jpg"
        cv2.imwrite(temp_path, original, [cv2.IMWRITE_JPEG_QUALITY, quality])
        compressed = cv2.imread(temp_path)

        # Calculate ELA
        ela = cv2.absdiff(original, compressed)
        ela_gray = cv2.cvtColor(ela, cv2.COLOR_RGB2GRAY)

        # Improve visibility with CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        ela_gray = clahe.apply(ela_gray)

        return original, ela_gray

    # --------- Step 2: Detect Forgery with Edge Detection ---------
    def detect_forgery_with_edges(image_path, mask_path="detected_mask.png", ela_quality=85, 
                                canny_thresh1=30, canny_thresh2=100, min_contour_area=300):
        original, ela = apply_ela(image_path, ela_quality)

        # Edge detection
        edges = cv2.Canny(ela, canny_thresh1, canny_thresh2)

        # Morphological operations to enhance edges
        kernel = np.ones((5,5), np.uint8)
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        dilated_edges = cv2.dilate(closed_edges, kernel, iterations=2)

        # Find contours of forgery regions
        result = original.copy()
        mask = np.zeros_like(edges)  # Black mask to store forgery regions
        contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_contour_area:
                cv2.drawContours(result, [cnt], 0, (0, 255, 0), 2)  # Green contours
                cv2.drawContours(mask, [cnt], -1, 255, thickness=cv2.FILLED)  # White mask for inpainting

        # Save mask for inpainting
        cv2.imwrite(mask_path, mask)

        return original, ela, edges, dilated_edges, result, mask_path

    # --------- Step 3: Deep Learning-Based Inpainting ---------
    def inpaint_image(image_path, mask_path, output_path="restored_image.png", checkpoint="pretrained/states_tf_places2.pth"):
        # Load pre-trained inpainting model
        generator_state_dict = torch.load(checkpoint)['G']
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        generator = Generator(cnum_in=5, cnum=48, return_flow=False).to(device)
        generator.load_state_dict(generator_state_dict, strict=True)

        # Load image and mask
        image = Image.open(image_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")  # Convert mask to grayscale

        # Convert to tensor
        image = T.ToTensor()(image)
        mask = T.ToTensor()(mask)

        _, h, w = image.shape
        grid = 8

        image = image[:, :h//grid*grid, :w//grid*grid].unsqueeze(0)
        mask = mask[0:1, :h//grid*grid, :w//grid*grid].unsqueeze(0)

        # Normalize image and mask
        image = (image * 2 - 1.).to(device)
        mask = (mask > 0.5).float().to(device)

        image_masked = image * (1.-mask)
        ones_x = torch.ones_like(image_masked)[:, 0:1, :, :]
        x = torch.cat([image_masked, ones_x, ones_x * mask], dim=1)

        with torch.no_grad():
            _, x_stage2 = generator(x, mask)

        # Restore inpainted image
        image_inpainted = image * (1. - mask) + x_stage2 * mask

        # Convert to PIL and save
        img_out = ((image_inpainted[0].permute(1, 2, 0) + 1) * 127.5).byte().cpu().numpy()
        img_out = Image.fromarray(img_out)
        img_out.save(output_path)

        print(f"Restored image saved as: {output_path}")

    # --------- Step 4: Execute the Full Pipeline ---------
       
    image_path = file_path

            # Step 1 & 2: Detect forgery and generate mask
    original, ela, edges, processed_edges, result, mask_path = detect_forgery_with_edges(image_path)

            # Step 3: Use Deep Learning Model for Inpainting
    inpaint_image(image_path, mask_path, output_path="final_restored_image.png")

            # Step 4: Display results
    plt.figure(figsize=(20, 15))

    plt.subplot(1, 5, 1)
    plt.imshow(original)
    plt.title("Uploaded Image")
    plt.axis('off')

    plt.subplot(1, 5, 2)
    plt.imshow(ela, cmap='gray')
    plt.title("ELA Analysis with CLAHE")
    plt.axis('off')

    plt.subplot(1, 5, 3)
    plt.imshow(edges, cmap='gray')
    plt.title("Canny Edge Detection")
    plt.axis('off')

    plt.subplot(1, 5, 4)
    plt.imshow(result)
    plt.title("Forgery Detection Result")
    plt.axis('off')

    restored_image = Image.open("final_restored_image.png")
    plt.subplot(1, 5, 5)
    plt.imshow(restored_image)
    plt.title("Restored Image (Deep Inpainting)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()


    return JsonResponse({"image": "http://localhost:8000/media/images/output.png"})
