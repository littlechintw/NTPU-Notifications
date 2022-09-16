from func import *

if __name__ == '__main__':
    init_sqlite()
    items = getItem()
    proccess_item(items)