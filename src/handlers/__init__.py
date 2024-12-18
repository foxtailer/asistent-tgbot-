from service.start import start_router

from wordsbook.add_cmd import add_router
from wordsbook.del_cmd import del_router
from wordsbook.show_cmd import show_router

from games.shuffle import shuffle_router
from games.test import test_router
from games.test10 import test10_router


routers_list = [
    start_router,

    add_router,
    del_router,
    show_router,
    
    shuffle_router,
    test10_router,
    test_router,
]


__all__ = [
    "routers_list",
]
