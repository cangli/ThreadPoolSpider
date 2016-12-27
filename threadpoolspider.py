import threading
import queue
import time
import requests


class ThreadPool(object):
    def __init__(self, work_queue, thread_num=10, thread_block=False):
        self.work_queue = work_queue
        self.threads = []
        self.thread_block = threading.Event()
        if thread_block is True:
            self.thread_block.clear()
        else:
            self.thread_block.set()
        self.__init_thread_pool(thread_num)

    """
        初始化线程
    """

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            self.threads.append(JustThread(self.work_queue, self.thread_block))
    """
        初始化工作队列
    """

    # def add_job(self, func, *args):
    # self.work_queue.put((func))  # 任务入队，Queue内部实现了同步机制

    """
        优先任务已完成
    """

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

    """
        等待所有线程运行完毕
    """

    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive():
                item.join()


class JustThread(threading.Thread):
    def __init__(self, work_queue, thread_block):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.thread_block = thread_block
        self.start()

    def run(self):
        # 死循环，从而让创建的线程在一定条件下关闭退出
        while True:
            try:
                do, *args = self.work_queue.get(block=True, timeout=3)  # 任务异步出队，Queue内部实现了同步机制
                do(*args)
                self.work_queue.task_done()  # 通知系统任务完成
            except queue.Empty:
                if self.thread_block.isSet() is False:
                    continue
                else:
                    print(threading.current_thread(), " quit.")
                    break
            except Exception as e:
                print(str(e))
                print("the function is", do.__name__, "the args are", str(*args))
                break


def MakeRequests(url):
    re = requests.get(url)
    print(threading.current_thread(), url)


if __name__ == '__main__':
    urls = ["http://www.baidu.com", "http://www.bing.com", "http://www.qq.com", "http://www.baidu.com", "http://www.bing.com",
            "http://www.qq.com", "http://www.baidu.com", "http://www.bing.com", "http://www.qq.com", "http://www.qq.com"]
    q = queue.Queue()
    for url in urls:
        q.put((MakeRequests, url))
    start = time.time()
    task = ThreadPool(q, 10)
    # task.thread_unblock()
    task.wait_allcomplete()
    end = time.time()
    print('time', end - start)
    print("finished")
