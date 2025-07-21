import uuid, sys, datetime
from common.sound import Master as sm
from common.io import IO
from common.utils import Log
from config import *

class Storage:

    """
    Мастер управления с данными на складе и существующими товарами

    LoadProducts <- () -> Все продукты в JSON.
    Change <- (имя продукта, ключ для заполнения, новое значение, файл(н)) -> Нечего
    NewProduct <- (Имя продукта, цена, начальное количество, файл(н)) -> Нечего
    Delete <- (Имя товара, файл(н)) -> Нечего
    """

    @staticmethod
    def LoadProducts():
        try:
            path = DATA_DIR / "storage.json"
            products = IO.LoadJSON(path)
            return products
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))



    @staticmethod
    def Change(product_name: str, field: str, new_value, file: str = "storage.json"):

        """
        :param product_name: Имя продукта
        :param field: Ключ для заполнения
        :param new_value: Новое значение
        :param file: Файл (по умолчанию storage.json)
        :return: Нечего
        """

        path = DATA_DIR / file
        data = IO.LoadJSON(path)

        Log.INFO(f"Changing data for {product_name}, {field} -> {new_value}, file={file}")
        try:
            if product_name not in data:
                raise KeyError(f"Товара '{product_name}' нет в списке.")

            if field not in data[product_name]:
                raise KeyError(f"У товара '{product_name}' нет поля '{field}'.")

            data[product_name][field] = new_value
            IO.DumpJSON(data, path)
            sm.Play("success")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))


    @staticmethod
    def Delete(product_name: str, file: str = "storage.json"):
        """
        :param product_name: Имя продукта
        :param file: Имя файла (по умолчанию storage.json)
        :return: Нечего
        """

        Log.INFO(f"Deleting product named {product_name} in {file}")
        path = DATA_DIR / file
        data = IO.LoadJSON(path)
        try:
            if product_name not in data:
                raise KeyError(f"Товара '{product_name}' нет в списке.")
            del data[product_name]
            IO.DumpJSON(data, path)
            sm.Play("success")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def NewProduct(name: str, price: int, count: int, file: str = "storage.json"):
        """
        :param name: Имя товара
        :param price: Цена
        :param count: Количество
        :param file: Файл (по умолчанию storage.json)
        :return: Нечего
        """
        path = DATA_DIR / file
        data = IO.LoadJSON(path)

        Log.INFO(f"Adding new product with ({name}, {price}, {count}) into {file}")

        try:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Название товара должно быть непустой строкой.")
            if not isinstance(price, (int, float)) or price < 0:
                raise ValueError("Цена должна быть положительным числом.")
            if not isinstance(count, int) or count < 0:
                raise ValueError("Количество должно быть целым неотрицательным числом.")
            if name in data:
                raise ValueError(f"Товар '{name}' уже существует.")
            data[name] = {
                "price": price,
                "count": count
            }

            IO.DumpJSON(data, path)
            Log.INFO(f"Товар {name} успешно добавлен.")
            sm.Play("success")

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def GetProductsByName(product_name: str):
        products = IO.LoadJSON(DATA_DIR / "storage.json")
        result = []
        for key, value in products.items():
            if product_name.lower() in key.lower(): result.append({key: value})

        return result

    @staticmethod
    def GetTotalProductsSum():

        file = DATA_DIR / "storage.json"
        data = IO.LoadJSON(file)
        total = sum([value["price"] for value in data.values()])
        return total

class Sales:

    """
    Мастер для продажи товара

    Sale <- (Имя товара, кол-во, файл(н)) -> Продажа товара
    Refund <- (ID товара) -> Возврат продажи товара

    """

    @staticmethod
    def Sale(product_name: str, count: int, file: str = "sales.json"):
        """
        :param product_name: Имя продукта
        :param count: Количество
        :param file: Файл (по умолчанию sales.json)
        :return:
        """

        try:
            path = DATA_DIR / file
            f = IO.LoadJSON(path)
            storage_path = DATA_DIR / "storage.json"
            data = IO.LoadJSON(storage_path)
            date = datetime.datetime.now().isoformat()
            _id = str(uuid.uuid4())

            Log.INFO(f"Sale {product_name} for {count} times. Generated id = {_id}, into {file}")

            if product_name not in data:
                raise NameError(f"Товар '{product_name}' не найден на складе.")

            current_count = data[product_name]["count"]
            if count > current_count:
                raise ValueError(f"Недостаточно товара '{product_name}'. В наличии: {current_count}, требуется: {count}")
            data[product_name]["count"] -= count
            IO.DumpJSON(data, storage_path)
            obj = {
                "date": date,
                "price": data[product_name]["price"],
                "count": count,
                "name": product_name
            }
            f[_id] = obj
            IO.DumpJSON(f, path)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))

    @staticmethod
    def Refund(_id: str):
        """
        :param _id: ID товара str(uuid.uuid4())
        :return: Нечего
        """

        try:
            Log.INFO(f"Refunding sale #{_id}")
            sale_data = IO.LoadJSON(DATA_DIR / "sales.json")
            dat = sale_data[_id]
            price, count, name = dat["price"], dat["count"], dat["name"]
            storage_data = IO.LoadJSON(DATA_DIR / "storage.json")

            if name not in storage_data:
                storage_data[name] = {"price": price, "count": count}
                del sale_data[_id]
                IO.DumpJSON(sale_data, DATA_DIR / "sales.json")
                IO.DumpJSON(storage_data, DATA_DIR / "storage.json")

            else:
                storage_data[dat["name"]]["count"] += count
                del sale_data[_id]
                IO.DumpJSON(sale_data, DATA_DIR / "sales.json")
                IO.DumpJSON(storage_data, DATA_DIR / "storage.json")
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            Log.FATAL((exc_type, exc_value, exc_traceback))


