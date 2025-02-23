import random
import os
import datetime

from PIL import Image

class LightImage(object):
    def __init__(self, image_info, template, org=None):
        self.image_info=image_info
        self.template = template
        self.org = org

    def draw_image(self):
        if not os.path.exists(f'img/{self.org}'): os.makedirs(f'img/{self.org}')
        image: Image = Image.new('RGBA', (self.image_info['size']))
        image = Image.alpha_composite(image, Image.open(
            f'img_templates/{self.image_info['dir']}/back/{random.choice(self.image_info['elements']['back'])}').convert('RGBA'))
        for element_name, element_value in self.image_info['elements']['main'].items():
            for key, value in element_value.items():
                path = f'img_templates/{self.image_info['dir']}/{element_name}/{value['image'][self.template[key]]}'
                open_image = Image.open(path).convert("RGBA")
                image.paste(open_image, (value['position']['x'], value['position']['y']), open_image)

        for element_name, element_value in self.image_info['elements']['additional'].items():
            if element_value['random'] == 0:
                for key, value in element_value['items'].items() :
                    path = f'img_templates/{self.image_info['dir']}/{element_name}/{value['image']}'
                    image.paste(Image.open(path), (value['position']['x'], value['position']['y']), Image.open(path))
            else:
                folder_path = f'img_templates/{self.image_info['dir']}/{element_name}/'
                images = os.listdir(folder_path)
                for position in element_value['position']:
                    image_path = folder_path + random.choice(images)
                    image.paste(Image.open(image_path), position, Image.open(image_path))

        image_name = f'img/org1/{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}-{self.image_info['name']}.png'
        image.save(image_name)
