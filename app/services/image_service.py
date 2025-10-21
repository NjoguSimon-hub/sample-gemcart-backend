from flask import current_app
import cloudinary
import cloudinary.uploader
from PIL import Image
import io
import base64

def upload_image(image_data, folder='products'):
    """
    Upload image to Cloudinary with optimization
    """
    try:
        if not current_app.config.get('CLOUDINARY_CLOUD_NAME'):
            return None, 'Cloudinary not configured'
        
        # If image_data is base64, decode it
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            # Remove data:image/jpeg;base64, prefix
            image_data = image_data.split(',')[1]
            image_data = base64.b64decode(image_data)
        
        # Optimize image using PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Resize if too large
        max_size = (1200, 1200)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Save optimized image to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            output.getvalue(),
            folder=folder,
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'fill', 'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
        
        return result['secure_url'], result['public_id']
    
    except Exception as e:
        current_app.logger.error(f'Image upload failed: {str(e)}')
        return None, str(e)

def delete_image(public_id):
    """
    Delete image from Cloudinary
    """
    try:
        if not current_app.config.get('CLOUDINARY_CLOUD_NAME'):
            return False
        
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    
    except Exception as e:
        current_app.logger.error(f'Image deletion failed: {str(e)}')
        return False