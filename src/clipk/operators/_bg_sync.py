import threading
import functools

THREAD_LIMIT = 2
_bg_threads = []


def spawn_bg_proc(func, *args, **kwargs) -> threading.Thread | None:
    if len(_bg_threads) >= THREAD_LIMIT:
        print("max thread limit reached skipping")
        return None

    t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    _bg_threads.append(t)
    t.start()
    return t


def run_in_backgroand(func):
    """makes a function be able to run in background"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return spawn_bg_proc(func, *args, **kwargs)

    return wrapper


def wait():
    for t in _bg_threads:
        t.join()
    _bg_threads.clear()
