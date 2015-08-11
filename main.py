from io import BytesIO
import os

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
import tornado.ioloop
import tornado.web



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def post(self):

        fp = BytesIO(self.request.files['image'][0]['body'])

        img = Image.open(
            fp
        ).convert('RGBA')
        overlay = Image.new('RGBA', img.size, (255,255,255,0))

        num_stripes = 5
        stripe_height = int(img.height / num_stripes)

        stripes = (
            (0, 0, img.width, stripe_height),
            (0, stripe_height, img.width, stripe_height*2),
            (0, stripe_height*2, img.width, stripe_height*3),
            (0, stripe_height*3, img.width, stripe_height*4),
            (0, stripe_height*4, img.width, img.height),
        )

        colors = (
            (255, 40, 255, 128),
            (255, 80, 255, 128),
            (255, 110, 255, 128),
            (255, 140, 255, 128),
            (255, 170, 255, 128),
        )

        for stripe, color in zip(stripes, colors):
            draw = ImageDraw.Draw(overlay)
            draw.rectangle(stripe, fill=color)

        font = ImageFont.truetype("DejaVuSans.ttf", int(img.height/2))

        text_box = Image.new('RGBA', img.size, (0,0,0,0))
        text_draw = ImageDraw.Draw(text_box)
        text_draw.text((0, 0), "LIFE", font=font)
        text_min_x, text_min_y, text_max_x, text_max_y = text_box.getbbox()
        text_width = text_max_x - text_min_x
        text_height = text_max_y - text_min_y
        offset_x = ((img.width - text_width) / 2) - text_min_x
        offset_y = ((img.height - text_height) / 2) - text_min_y

        draw.text((offset_x, offset_y), "LIFE", font=font)


        # img.save('output.jpg')
        combined = Image.alpha_composite(img, overlay)
        output = BytesIO()
        combined.save(output, format='jpeg')
        output.seek(0)

        self.set_header('Content-Type', self.request.files['image'][0].get('content_type'))
        self.write(output.read())



app = tornado.web.Application([
    (r'/', MainHandler),
])

if __name__ == '__main__':
    app.listen(os.getenv('PORT', 5000))
    tornado.ioloop.IOLoop.current().start()
