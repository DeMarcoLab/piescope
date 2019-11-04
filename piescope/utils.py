import skimage.io as io


def save_image(image, dest):
    io.imsave(dest, image)
