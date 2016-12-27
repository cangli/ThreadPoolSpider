import threading
import queue
import time
import requests
import multiprocessing


class ThreadPool(object):
    def __init__(self, work_queue, thread_num=10, thread_block=False):
        self.work_queue = work_queue
        self.thread_pool = multiprocessing.Pool(thread_num)
        self.thread_block = threading.Event()
        if thread_block is True:
            self.thread_block.clear()
        else:
            self.thread_block.set()
        self.run()

    def thread_unblock(self):
        self.thread_block.set()
    """
        优先任务执行中
    """

    def thread_block(self):
        self.thread_block.clear()
    """
        检查剩余队列任务
    """

    def check_queue(self):
        return self.work_queue.qsize()

    def run(self):
        while True:
            try:
                do, *args = self.work_queue.get(block=True, timeout=3)  # 任务异步出队，Queue内部实现了同步机制
                self.thread_pool.apply_async(do, args, callback=self.work_queue.task_done())
                # 通知系统任务完成
            except queue.Empty:
                if self.thread_block.isSet() is False:
                    continue
                else:
                    print(threading.current_thread(), " quit.")
                    break
            except Exception as e:
                self.work_queue.task_done()
                print(str(e))
                print("the function is", do.__name__, "the args are", str(*args))
                break

    def wait_allcomplete(self):
        self.work_queue.join()
        self.thread_pool.close()
        self.thread_pool.join()


def MakeRequests(url):
    re = requests.get(url)
    print(threading.current_thread(), url)


if __name__ == '__main__':
    urls = ["http://www.baidu.com", "http://www.bing.com", "http://www.qq.com", "http://www.baidu.com", "http://www.bing.com",
            "http://www.qq.com", "http://www.baidu.com", "http://www.bing.com", "http://www.qq.com", ]
    q = queue.Queue()
    for url in urls:
        q.put((MakeRequests, url))
    start = time.time()
    task = ThreadPool(q, 10, False)
    # task.thread_unblock()
    task.wait_allcomplete()
    end = time.time()
    print('time', end - start)
    print("finished")
