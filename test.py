from draw_image2 import LightImage

light_template = {'o_plus': 'red', 'o_minus':'green',
                  'a_plus': 'red', 'a_minus':'green',
                  'b_plus': 'red', 'b_minus':'green',
                  'ab_plus': 'red', 'ab_minus':'green'}

image = LightImage('color_drops', light_template, 'org1')
image.draw_image()