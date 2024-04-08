from typing import List

class Product:
    def __init__(self, title: str, price: float, images: List[str]):
        if not isinstance(title, str):
            raise ValueError("Title must be a string.")
        if not (isinstance(price, int) or isinstance(price, float)):
            raise ValueError("Price must be a numeric type.")
        if not (isinstance(images, list) and all(isinstance(i, str) for i in images)):
            raise ValueError("Images must be a list of strings.")

        self._title = title
        self._price = price
        self._images = images

    @property
    def title(self):
        return self._title

    @property
    def price(self):
        return self._price

    @property
    def images(self):
        return self._images.copy()  # return a copy to prevent external modifications

    def __repr__(self):
        return f"Product(title={self.title}, price={self.price}, images={len(self.images)} images)"