import logging
from utils.minio_utils import get_presigned_url

# Configure logging for this module.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def load_hand_models_sync() -> dict:
    """
    Synchronously loads hand model URLs from MinIO.

    Returns:
        dict: A dictionary containing pre-signed URLs for:
            - 'skeleton_model': URL for the skeleton hand model.
            - 'flesh_model': URL for the flesh hand model.
    
    Raises:
        Exception: Propagates any exception encountered during URL generation.
    """
    try:
        skeleton_model_url = get_presigned_url("skeleton_hand.glb")
        flesh_model_url = get_presigned_url("flesh_hand.glb")
        logger.info("Generated presigned URL for skeleton_hand.glb: %s", skeleton_model_url)
        logger.info("Generated presigned URL for flesh_hand.glb: %s", flesh_model_url)
        return {
            "skeleton_model": skeleton_model_url,
            "flesh_model": flesh_model_url
        }
    except Exception as e:
        logger.exception("Error loading hand models from MinIO: %s", e)
        raise e

if __name__ == "__main__":
    models = load_hand_models_sync()
    print("Loaded hand models:", models)
