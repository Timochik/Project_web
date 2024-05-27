import io
import uuid
import qrcode
import cloudinary
import cloudinary.uploader

from src.conf.config import settings


async def get_qr_code_by_url(url: str, service: cloudinary=cloudinary) -> str:
    """
    The get_qr_code_by_url function takes a url as an argument and returns the URL of a QR code image.
    
    :param url: str: Specify the url that will be encoded in the qr code
    :param service: cloudinary: Specify the cloudinary service that will be used to upload the image
    :return: The url of a qr code image
    :doc-author: Trelent
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    b = io.BytesIO()
    img.save(b, 'png')
    img_bytes = b.getvalue()

    service.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    public_id = f'{settings.cloudinary_folder_name}/qrcode/{uuid.uuid4()}'

    service.uploader.upload(
        img_bytes,
        public_id=public_id,
        overwrite=True
    )

    src_url = service.CloudinaryImage(public_id).build_url()

    return src_url


async def delete_qr_code_by_url(url: str, service: cloudinary=cloudinary) -> None:
    """
    The delete_qr_code_by_url function deletes a QR code from Cloudinary.
    If file not founr raises FileNotFoundError error.
        
    
    
    :param url: str: Specify the url of the qr code to be deleted
    :param service: cloudinary: Specify the cloudinary service to use
    :return: None
    :doc-author: Trelent
    """
    filename = url.split("/")[-1]
    public_id = f'{settings.cloudinary_folder_name}/qrcode/{filename}'

    service.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    res = service.uploader.destroy(public_id=public_id)
    print(res)
    if res["result"] != "ok":
        raise FileNotFoundError(
            f"Cloudinary file with public ID '{public_id}' not found"
        )
