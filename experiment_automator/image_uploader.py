from experiment_automator.exceptions import ImageUploaderException
from experiment_automator.constants import Constants
from experiment_automator.oauth_client import OAuthClient


class ImageUploader:
    def __init__(self, debug, image_uploader_config):
        self.debug = debug

        if image_uploader_config is None:
            raise ImageUploaderException("%s - Image uploader config is None. Please specify api key in config!" % self.__class_name())

        self.image_uploader_config = image_uploader_config

    def __class_name(self):
        return self.__class__.__name__

    def get_session(self, callback, **params):
        return OAuthClient(self.image_uploader_config.get(Constants.KEY_OAUTH)).connect(callback, **params)


class FlickrImageUploader(ImageUploader):
    def __init__(self, debug, image_uploader_config):
        super().__init__(debug, image_uploader_config)
        self.session = super().get_session(Constants.KEY_OAUTH_CALLBACK_OOB, perms="write")

    # TODO Title etc. other parameters will be added
    def upload_image(self, image_path):
        files = {
            "photo": open(image_path, 'rb'),
        }

        params = {
            "title": "Test",
            "is_public": 0
        }
        return self.session.post(self.image_uploader_config.get(Constants.KEY_SLACK_IMAGE_SERVICE_UPLOAD_URL),
                params=params, files=files)