import wand.image
import wand.display
import wand.color

import PIL.Image
import io

from typing import List, Union
import numpy as np


def convert_pdf(file: bytes, resolution=50)-> List[bytes]:
    """
        Convert a PDF into lihttp://docs.wand-py.org/en/0.4.1/wand/display.htmlst of images in bytes format.
        The function removes the alpha channel from the image and
        replaces it with a white background.
    """

    all_pages = wand.image.Image(blob=file, resolution=resolution)

    pages = list()

    for i, page in enumerate(all_pages.sequence):
        with wand.image.Image(page) as img:
            img.format = 'png'
            img.background_color = wand.color.Color('white')
            img.alpha_channel = 'remove'

            pages.append(img.make_blob())

    return pages


def unify_pages(pages: List[bytes])-> bytes:

        parss = [page_to_array(pg) for pg in pages]

        npars = [without_padding(pg) for pg in parss]

        return array_to_page(np.concatenate(npars))


def page_to_array(page: bytes)-> np.ndarray:
    """
    takes bytes image and converts it through PIL library to numpy array
    """
    pimg = PIL.Image.open(io.BytesIO(page))
    return np.asarray(pimg)


def array_to_page(array: np.ndarray)->bytes:
    """
    does exact opposite of page_to_array
    """
    img = PIL.Image.fromarray(np.uint8(array))

    faux_file = io.BytesIO()
    img.save(faux_file, 'png')
    return faux_file.getvalue()


def without_padding(arr: np.ndarray)->np.ndarray:
    """
    finds lines closest to sides, that aren't PURELY white and cuts all the whites
    :param arr: array with white blocks on sides
    :return : modified array
    """
    cx = 0                # leftmost white line
    cy = 0                # topmost white line
    mx = arr.shape[0]-1   # rightmost white line
    my = arr.shape[1]-1   # downmost white line

    for x in range(mx):
        if arr[x].mean() != 255:
            cx = x-1
            break
    for y in range(my):
        if arr[..., y].mean() != 255:
            cy = y-1
            break
    for xx in range(mx, cx, -1):
        if arr[xx].mean() != 255:
            mx = xx+1
            break
    for yy in range(my, cy, -1):
        if arr[..., yy].mean() != 255:
            my = yy+1
            break

    block = divide_block(arr, 'h', [cx, mx])[1:2]
    nar = np.uint8(np.concatenate(tuple(block)))

    block = divide_block(nar, 'v', [cy, my])[1:2]
    mar = np.uint8(np.concatenate(tuple(block)))

    return mar


def divide_block(arr: np.ndarray, rot: str, lines:Union[list, tuple])-> List[np.ndarray]:
    block = list()

    # find all horizontal lines

    block.append(arr[0:lines[0]])  # add first block

    lines.append(arr.shape[1])  # add last block

    for idx, itm in enumerate(lines[:-1]):

        if rot == 'h':
            block.append((arr[itm:lines[idx+1]]))
        else:
            block.append((arr[..., itm:lines[idx + 1]]))

    return block


if __name__ == '__main__':

    png = convert_pdf(open('./sups/17092018/f5f09ebb5307b773b770c7bd358b1e299ae0aa325400884ddd7fcf878fef6790.pdf', 'rb').read())[0]
    ar = page_to_array(png)
    ar.setflags(write=True)
    print(ar.shape)

    wand.display.display(wand.image.Image(blob=array_to_page(without_padding(ar))))
