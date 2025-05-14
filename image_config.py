from typing import Dict
from pydantic import BaseModel

class Position(BaseModel):
    x: int
    y: int

class GroupSensitiveElement(BaseModel):
    position: Position
    image: dict

class GroupSensitiveImage(BaseModel):
    """
    Обязательный набор элементов, зависящих от цвета группы крови
    """
    o_minus: GroupSensitiveElement
    o_plus: GroupSensitiveElement
    a_minus: GroupSensitiveElement
    a_plus: GroupSensitiveElement
    b_minus: GroupSensitiveElement
    b_plus: GroupSensitiveElement
    ab_minus: GroupSensitiveElement
    ab_plus: GroupSensitiveElement

class NoneGroupSensitiveElementPositional(BaseModel):
    position: Position
    image: str

class NoneGroupSensitiveImagePositional(BaseModel):
    items:Dict[str, NoneGroupSensitiveElementPositional]

class NoneGroupSensitiveImageRandom(BaseModel):
    position: list[tuple[int, int]]

class AdditionalElements(BaseModel):
    """
    Элементы, которые не изменяются от цвета группы крови и могут отсутствовать
    positional: Элементы с точно заданными значениями. Например, название групп крови или логотип.
    random: Элементы со значениями из набора, изменяемые "украшательства". Например, есть несколько цветков,
    которые выбираются случайным образом, но в заданных координатах.
    """
    positional: Dict[str, NoneGroupSensitiveImagePositional] | None = None
    random: Dict[str, NoneGroupSensitiveImageRandom] | None = None

class Elements(BaseModel):
    """
    Основные элементы изображения.
    back: Подложка
    main: Элементы которые изменяются от цвета группы крови
    additional: Элементы которые НЕ изменяются от цвета группы крови
    """
    back: list[str]
    main: Dict[str, GroupSensitiveImage]
    additional: AdditionalElements

class ImageConfig(BaseModel):
    name: str
    dir: str
    size: tuple[int, int]
    elements: Elements


# image_config = ImageConfig.model_validate_json(input_json)
# image_config.model_dump_json(indent=4)