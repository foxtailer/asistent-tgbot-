from .callback.play import play_call_router
from .callback.show import show_call_router
from .callback.shuffle import shuffle_call_router

from .commands.add_cmd import add_router
from .commands.del_cmd import del_router
from .commands.show_cmd import show_router
from .commands.shuffle import shuffle_router
from .commands.start import start_router
from .commands.test import test_router

from .msg.play import play_msg_router
from .msg.shuffle import shuffle_msg_router


routers_list = [
    start_router,
    add_router,
    del_router,
    show_router,
    shuffle_router,
    test_router,

    play_msg_router,
    shuffle_msg_router,

    shuffle_call_router,
    play_call_router,
    show_call_router,
]



__all__ = [
    "routers_list",
]
