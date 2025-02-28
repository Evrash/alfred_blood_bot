from draw_image2 import LightImage

light_template = {'o_plus': 'red', 'o_minus':'green',
                  'a_plus': 'yellow', 'a_minus':'red',
                  'b_plus': 'green', 'b_minus':'yellow',
                  'ab_plus': 'green', 'ab_minus':'red'}

image = LightImage('color_drops', light_template, 'org1')
image.draw_image()