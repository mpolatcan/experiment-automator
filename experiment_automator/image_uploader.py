from experiment_automator.exceptions import ImageUploaderException
from experiment_automator.constants import SlackConstants, OAuthConstants, FlickrConstants, OtherConstants
from experiment_automator.oauth_client import OAuthClient
from experiment_automator.utils import DebugLogCat
from xml.etree import ElementTree


class ImageUploader:
    def __init__(self, debug, image_uploader_config):
        self.debug = debug

        if image_uploader_config is None:
            raise ImageUploaderException("%s - Image uploader config is None. Please specify api key in config!" % self.__class_name())

        self.image_uploader_config = image_uploader_config
        self.oauth_config = image_uploader_config.get(OAuthConstants.KEY_OAUTH)

        # If Flickr service defined get configurations from Constants
        if not (self.oauth_config is None) and self.oauth_config.get(OAuthConstants.KEY_OAUTH_SERVICE_NAME) == OtherConstants.IMAGE_SERVICE_FLICKR:
            self.oauth_config[OAuthConstants.KEY_OAUTH_REQUEST_TOKEN_URL] = FlickrConstants.FLICKR_OAUTH_REQUEST_TOKEN_URL
            self.oauth_config[OAuthConstants.KEY_OAUTH_AUTHORIZATION_URL] = FlickrConstants.FLICKR_OAUTH_AUTHORIZATION_URL
            self.oauth_config[OAuthConstants.KEY_OAUTH_ACCESS_TOKEN_URL] = FlickrConstants.FLICKR_OAUTH_ACCESS_TOKEN_URL
            self.oauth_config[OAuthConstants.KEY_OAUTH_BASE_URL] = FlickrConstants.FLICKR_OAUTH_BASE_URL

            self.image_uploader_config[SlackConstants.KEY_SLACK_IMAGE_SERVICE_UPLOAD_URL] = FlickrConstants.FLICKR_UPLOAD_URL

    def __class_name(self):
        return self.__class__.__name__

    def get_session(self, callback, **params):
        return OAuthClient(self.debug, self.image_uploader_config.get(OAuthConstants.KEY_OAUTH)).connect(callback, **params)


class FlickrImageUploader(ImageUploader):
    def __init__(self, debug, image_uploader_config):
        super().__init__(debug, image_uploader_config)
        self.session = super().get_session(OAuthConstants.KEY_OAUTH_CALLBACK_OOB, perms="write")

    def __class_name(self):
        return self.__class__.__name__

    def __get_image_static_url(self, photo_id, image_type):
        data = {
            "photo_id": photo_id,
            "method": FlickrConstants.FLICKR_GET_IMAGE_SIZES_METHOD
        }

        response = self.session.post(self.oauth_config.get(OAuthConstants.KEY_OAUTH_BASE_URL), data=data).text

        sizes = {}
        for size in ElementTree.fromstring(response).find('sizes').findall('size'):
            sizes[size.attrib["label"]] = size.attrib["source"]

        return sizes[image_type]

    def upload_image(self, image_path, image_type):
        DebugLogCat.log(self.debug, self.__class_name(), "Uploading image \"%s\"" % image_path)

        files = {
            "photo": open(image_path, 'rb'),
        }

        photo_id = ElementTree.fromstring(self.session.post(self.image_uploader_config.get(SlackConstants.KEY_SLACK_IMAGE_SERVICE_UPLOAD_URL), files=files).text).find("photoid").text

        if photo_id is None:
            DebugLogCat.log(self.debug, self.__class_name(), "Image upload could not be completed!" % photo_id)
        else:
            DebugLogCat.log(self.debug, self.__class_name(), "Image upload completed. Photo id: \"%s\" !" % photo_id)

        return self.__get_image_static_url(photo_id, image_type)
