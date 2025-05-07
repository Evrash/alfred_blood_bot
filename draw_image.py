import random
import os
import datetime
from pathlib import Path

from PIL import Image
from image_config import ImageConfig
from config import settings


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
        self.image_name: Path|None = None

    # def paste_element_on_image(self, image:Image, element_path: Path, position:tuple[int, int]):
    #     open_image = Image.open(element_path).convert('RGBA')
    #     image.paste(open_image, position, open_image)

    def draw_image(self):
        """
        Создаёт итоговое изображение. Берётся основа, на неё наносятся другие детали изображения.
        Передаётся строка содержащая цвет светофора для каждой группы крови.
        Изображения делятся на зависящие и не зависящие от группы крови.
        :return:
        """
        if not os.path.exists(settings.base_dir / f'img/{self.org}'):
            os.makedirs(settings.base_dir / f'img/{self.org}')
        template_path: Path =settings.base_dir / 'img_templates' / self.image_template.dir
        image: Image = Image.new('RGBA', self.image_template.size)
        image = Image.alpha_composite(image, Image.open(template_path / 'back' /
                                                        random.choice(self.image_template.elements.back)).convert('RGBA'))

        # Размещаем элементы, зависимые от шаблона
        for element_name, element_value in self.image_template.elements.main.items():
            for group, params in self.light_template.items():
                path =  template_path / f'{element_name}' / getattr(element_value,group).image[params]
                open_image = Image.open(path).convert('RGBA')
                position = (getattr(element_value,group).position.x, getattr(element_value,group).position.y)
                image.paste(open_image, position, open_image)

        # Размещаем элементы не зависимые от групп крови
        if self.image_template.elements.additional.positional:
            for elements_name, elements_value in self.image_template.elements.additional.positional.items():
                for element_name, element_value in elements_value.items.items():
                    path = template_path / f'{elements_name}' / f'{element_value.image}'
                    open_image = Image.open(path).convert('RGBA')
                    image.paste(open_image, (element_value.position.x, element_value.position.y), open_image)

        if self.image_template.elements.additional.random:
            for elements_name, elements_value in self.image_template.elements.additional.random.items():
                folder_path = template_path / f'{elements_name}/'
                images = os.listdir(folder_path)
                for position in elements_value.position:
                    path = folder_path / random.choice(images)
                    open_image = Image.open(path).convert('RGBA')
                    image.paste(open_image, position, open_image)

        image_name = (settings.base_dir / f'img/{self.org}'/
                      f'{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}-{self.image_template.name}.png')
        image.save(image_name)
        self.image_name = image_name
