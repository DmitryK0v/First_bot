from random import randint
from captcha.image import ImageCaptcha

captcha_length = 5


def generate_captcha_text():
    """Generate text for captcha image.
    Each picture should have different text."""
    nums = []
    for i in range(captcha_length):
        nums.append(str(randint(0, 9)))  # For the uniqueness of the text in the picture, we use random.
    captcha_text = ''.join(nums)
    return captcha_text


class Captcha:
    """Using library capthca"""
    captcha_text = ''
    captcha_image = None

    def __init__(self):
        image = ImageCaptcha(width=300, height=100)
        self.captcha_text = generate_captcha_text()
        self.captcha_image = image.generate(self.captcha_text)
