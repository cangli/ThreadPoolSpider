from __future__ import print_function
import gevent
from gevent import monkey
from gevent.pool import Pool
from gevent.event import Event
import queue
import time
import requests


monkey.patch_all()


class GeventPool(object):
    def __init__(self, work_queue, thread_num=10, block=False):
        self.greenlets = []
        self.work_queue = work_queue
        self.pool = Pool(thread_num)
        self.block = Event()
        if block is True:
            self.block.clear()
        else:
            self.block.set()
        self.run()

    def thread_unblock(self):
        self.block.set()
    """
        优先任务执行中
    """

    def thread_block(self):
        self.block.clear()
    """
        检查剩余队列任务
    """

    def check_queue(self):
        return self.work_queue.qsize()

    def run(self):
        while True:
            try:
                do, *args = self.work_queue.get(block=True, timeout=3)  # 任务异步出队，Queue内部实现了同步机制
                self.greenlets.append(self.pool.apply_async(do, args, callback=self.work_queue.task_done()))
                # 通知系统任务完成
            except queue.Empty:
                if self.block.isSet() is False:
                    continue
                else:
                    print(gevent.getcurrent(), " quit.")
                    break
            except Exception as e:
                self.work_queue.task_done()
                print(str(e))
                print("the function is", do.__name__, "the args are", str(*args))
                break

    def wait_allcomplete(self):
        self.work_queue.join()
        self.pool.join()
        for greenlet in self.greenlets:
            greenlet.join()


def MakeRequests(url):
    re = requests.get(url)
    print(gevent.getcurrent(), url)


if __name__ == '__main__':
    urls = ["http://www.baidu.com", "http://www.sina.com", "http://www.qq.com", "http://www.baidu.com", "http://www.sina.com",
            "http://www.qq.com", "http://www.baidu.com", "http://www.sina.com", "http://www.qq.com", ]
    q = queue.Queue()
    for url in urls:
        q.put((MakeRequests, url))
    start = time.time()
    task = GeventPool(q, 5, False)
    # task.thread_unblock()
    task.wait_allcomplete()
    end = time.time()
    print('time', end - start)
    print("finished")
