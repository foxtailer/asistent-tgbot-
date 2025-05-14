from .commands.start import start_router
from .commands.select_day import select_day_router

from .commands.add_cmd import add_router
from .commands.del_cmd import del_router
from .commands.show_cmd import show_router

from .commands.shuffle import shuffle_router
from .commands.test import test_router
from .msg.play_msg import play_msg_router

from .callback.shuffle import shuffle_call_router
from .callback.play import play_call_router


routers_list = [
    start_router,
    select_day_router,

    add_router,
    del_router,
    show_router,
    
    shuffle_router,
    test_router,
    play_msg_router,

    shuffle_call_router,
    play_call_router
]


__all__ = [
    "routers_list",
]
