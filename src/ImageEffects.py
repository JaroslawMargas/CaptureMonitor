from PIL import Image, ImageDraw


class ImageEffects:
    def __init__(self):
        pass

    def add_circle_to_image(self, rgba_image, x_pos, y_pos, radius, fill):
        ellipse_image = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))

        # draw ellipse there
        d = ImageDraw.Draw(ellipse_image)
        d.ellipse((x_pos - radius,
                   y_pos - radius,
                   x_pos + radius,
                   y_pos + radius),
                  fill=fill)

        # blend alpha screen shot with cursor point
        out = Image.alpha_composite(rgba_image, ellipse_image)
        return out
