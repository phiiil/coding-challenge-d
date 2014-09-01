# -*- coding: utf8 -*-

import os
from multiprocessing import Pool
from PIL import Image, ImageFilter


SOURCE_FOLDER = './images'
DESTINATION_FOLDER = './processed_images'


def images():
    """ List files in the first level of the SOURCE_FOLDER
        returns a tuple of name, filename (full path)
    """
    root, dir, files = os.walk(SOURCE_FOLDER).next()
    for filename in files:
        name = os.path.splitext(filename)[0]
        yield name, os.path.join(root, filename)


def processed_filename(name):
    """ Using the name of the image, 
        returns the full path of the destination file """
    return DESTINATION_FOLDER + '/' + name + '.jpg'


class BusbudBanner(object):
    """Image manipulation functions for Busbud Banners."""

    @classmethod
    def load(cls, name, fp):
        """Load an image from a file pointer."""
        return (name, Image.open(fp))

    @classmethod
    def save(cls, filename, image):
        """Save an image to filename"""
        image.save(filename)

    @classmethod
    def scale_x(cls, name, image, size=1500, resample=Image.BICUBIC):
        """Scale the image along its x-axis to `size` pixels."""
        x, y = image.size
        scale = float(x) / size
        x_size = size
        y_size = int(round(y / scale))
        return name, image.resize((x_size, y_size), resample)

    @classmethod
    def blur(cls, name, image, radius=6):
        """Apply a Gaussian blur to image."""
        return name + '-blur', image.filter(ImageFilter.GaussianBlur(radius))

    @classmethod
    def crop_vertical(cls, image, y_1, y_2):
        """Crop an image along its y-axis."""
        x = image.size[0]
        return image.crop((0, y_1, x, y_2))

    @classmethod
    def crop_top(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the top."""
        return name + '-top', cls.crop_vertical(image, 0, height)

    @classmethod
    def crop_bottom(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the bottom."""
        y = image.size[1]
        return name + '-bottom', cls.crop_vertical(image, y - height, y)

    @classmethod
    def crop_vmiddle(cls, name, image, height=300):
        """Crop `image` to `height` pixels from the middle."""
        y = image.size[1]
        offset = (y - height) / 2
        return name + '-vmiddle', cls.crop_vertical(image, offset, y - offset)


def serial_image_processor(name_filename_tuple):
    """ Create a simple implementation of the required
        image processing tasks, we will use this as a
        functional reference"""
    name, filename = name_filename_tuple
    print "STARTING: %s" % name
    name, image = BusbudBanner.load(name, filename)
    print "scale_x %s" % name
    name, image = BusbudBanner.scale_x(name, image)
    print "blur %s" % name
    name, image = BusbudBanner.blur(name, image)
    # bottom crop
    print "crop_bottom %s" % name
    name_bottom, image_bottom = BusbudBanner.crop_bottom(name, image)
    print "save %s" % name_bottom
    BusbudBanner.save(processed_filename(name_bottom), image_bottom)
    # top crop
    name_top, image_top = BusbudBanner.crop_top(name, image)
    BusbudBanner.save(processed_filename(name_top), image_top)
    # vmiddle crop
    name_vmiddle, image_vmiddle = BusbudBanner.crop_vmiddle(name, image)
    BusbudBanner.save(processed_filename(name_vmiddle), image_vmiddle)
    print "COMPLETED: %s" % name
    return name


def process_images_serial():
    for name, filename in images():
        print "processing %s image %s" % (name, filename)
        serial_image_processor((name, filename))


def process_images_parallel():
    """ Use multiprocessing.Pool to process images in parallel in
        separate processes. """
    pool = Pool()
    result = pool.map_async(serial_image_processor, images())
    print result.get()


def main():
    #process_images_serial()
    process_images_parallel()


if __name__ == '__main__':
    main()
