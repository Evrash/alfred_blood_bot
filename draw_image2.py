import random
import os
import datetime

from PIL import Image
from image_config import ImageConfig
from config import settings
# from test import light_template


class LightImage(object):
    """
    Основной класс донорского светофора.
    """
    def __init__(self, image_template: str, light_template: dict, org: str=None):
        img_path = settings.base_dir / 'img_config' / f'{image_template}.json'
        with img_path.open('r') as f:
            json_config = f.read()
        self.image_template=ImageConfig.model_validate_json(json_config)
        self.light_template = light_template
        self.org = org

    def draw_image(self):
        """
        Создаёт итоговое изображение. Берётся основа, на неё наносятся другие изображения.
        Передаётся строка содержащая цвет светофора для каждой группы крови.
        Изображения делятся на зависящие и не зависящие от группы крови.
        :return:
        """
        if not settings.base_dir / f'img/{self.org}':
            os.makedirs(settings.base_dir / f'img/{self.org}')
        image: Image = Image.new('RGBA', self.image_template.size)
        image = Image.alpha_composite(image, Image.open(
            f'img_templates/{self.image_template.dir}/back/{random.choice(self.image_template.elements.back)}').convert('RGBA'))

        # Размещаем элементы, зависимые от шаблона
        # print(self.image_template.elements.main.items())
        for element_name, element_value in self.image_template.elements.main.items():
            print(element_name)
            print(element_value)
            print(type(element_value))
            for group, params in self.light_template.items():
                print(group)
                path = f'img_templates/{self.image_template.dir}/{element_name}/{getattr(element_value,group).image[params]}'
                open_image = Image.open(path).convert("RGBA")
                position = (getattr(element_value,group).position.x, getattr(element_value,group).position.y)
                image.paste(open_image, position, open_image)
            # for name in element_value:
            #     path = f'img_templates/{self.image_template.dir}/{element_name}/{name.self.light_template[str(name)]}'
            #     open_image = Image.open(path).convert("RGBA")
                # image.paste(open_image, (value.position.x, value.position.y), open_image)
            # for key, value in element_value.items():
            #     path = f'img_templates/{self.image_template.dir}/{element_name}/{value.image[self.light_template[key]]}'
            #     open_image = Image.open(path).convert("RGBA")
            #     image.paste(open_image, (value.position.x, value.position.y), open_image)

        # Размещаем элементы не зависимые от шаблона
        # for element_name, element_value in self.image_template.elements.additional.items():
        #     if element_value.random == 0: # Нужно ли размещать элементы в случайном порядке
        #         for key, value in element_value.items.items() :
        #             path = f'img_templates/{self.image_template.dir}/{element_name}/{value.image}'
        #             image.paste(Image.open(path), (value.position.x, value.position.y), Image.open(path))
        #     else:
        #         folder_path = f'img_templates/{self.image_template.dir}/{element_name}/'
        #         images = os.listdir(folder_path)
        #         for position in element_value.position:
        #             image_path = folder_path + random.choice(images)
        #             image.paste(Image.open(image_path), position, Image.open(image_path))

        image_name = f'img/org1/{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}-{self.image_template.name}.png'
        image.save(image_name)
