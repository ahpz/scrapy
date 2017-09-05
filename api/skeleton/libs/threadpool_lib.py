# coding:utf-8

import Queue
import threading
import sys
import time
import contextlib
import json
"""终止线程池任务"""
TERMINAL_TASK = object()
"""线程池实现"""
class CThreadPool(object):
    def __init__(self, max_num = 20):
        self.queue         = Queue.Queue()
        self.max_num       = max_num
        self.terminal      = False
        self.generate_list = []
        self.free_list     = []
        
    def thread_num(self):
        return len(self.generate_list);
    
    def run(self, func, args, callback = None):
        """
        :func 任务函数
        :args 任务参数
        :callback 任务运行结束后回调函数 回调函数有两个参数 任务函数执行状态 任务函数返回值 默认None
        """
        #线程池运行任务时 创建线程
        if len(self.free_list) == 0 and len(self.generate_list) < self.max_num:
            self.generate_thread()
        w = (func, args, callback,)
        self.queue.put(w) #添加任务
        
    def generate_thread(self):
        t = threading.Thread(target = self.call)
        #t.setDaemon(True) #表示此进程被init进程接管 当前进程结束后 仍然会继续运行
        t.start()
        
    def call(self):
        current_thread = threading.currentThread
        sys.stdout.write("thread:{0} start\n".format(threading.current_thread().getName()))
        self.generate_list.append(current_thread)
        task = self.queue.get()
        while task != TERMINAL_TASK:
            func, arguments, callback = task #解开 任务 分别取值
            try:
                result = func(*arguments)
                status = True
            except Exception as e:
                sys.stdout.write("exception:{0}\n".format(repr(e)))
                status = False
                result = e #
            if callback is not None:
                try:
                    callback(status, result)
                except Exception as e:
                    pass
                    sys.stdout.write("exception:{0}\n".format(repr(e)))
            if self.terminal:
                task = TERMINAL_TASK
            else:
                # self.free_list.append(current_thread)  #执行完毕任务，添加到闲置列表
                # event = self.q.get()  #获取任务
                # self.free_list.remove(current_thread)  # 获取到任务之后，从闲置列表中删除；不是元组，就不是任务                
                with self.worker_state(self.free_list, current_thread):
                    task = self.queue.get() #阻塞调用 非阻塞调用是 get_nowait
                    
        else:
            self.generate_list.remove(current_thread)
            sys.stdout.write("thread:{0} end\n".format(threading.current_thread().getName()))
            
    
    def close(self):
        """终止线程"""
        num = len(self.generate_list)
        while num:
            self.queue.put(TERMINAL_TASK)
            num -= 1
            
    def terminate(self):
        """终止线程 清空队列"""
        self.terminal = True
        while self.generate_list:
            self.queue.put(TERMINAL_TASK)
        """清空队列"""
        self.queue.empty() 
        
    @contextlib.contextmanager
    def worker_state(self, state_list, worker_thread):
        state_list.append(worker_thread)
        try:
            yield None
        finally:
            state_list.remove(worker_thread)
            
        
    
        
    
def work(i):
    #print( str(i) + '\n') #python 2.x 非线程安全函数输出会混乱
    import sys
    sys.stdout.write(str(i) + '\n')
   
if __name__ == "__main__":
    pool = CThreadPool(10)
    print "...." #此函数在多线程下无法运行 是非线程安全函数
    for item in xrange(50):
        #print item
        pool.run(func=work, args=(item,)) 
        
    time.sleep(5)
    pool.terminate();