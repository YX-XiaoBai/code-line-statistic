import os
import string
import time
import multiprocessing

from tkinter import filedialog
from tkinter import ttk
from tkinter import *


def python_lines_count(file_path, encoding):  # statistic python
    lines_count_python = 0
    flag_python = 0  # define flag, for skipping multiline comments
    try:
        with open(file_path, "r", encoding=encoding) as fp:
            for line in fp:
                if line.strip() == "'''" or line.strip()[1:4] == "'''" or line.strip()[
                        -3:] == "'''":  # multiline comment '''，cloud be character BOM
                    flag_python += 1  # the beginning of multiline comment，flag_python is odd number, the ending of multiline comment, flag_python is even number
                elif flag_python % 2 != 0:  # when flag_python is even number, continue
                    continue
                elif line.strip() in string.whitespace:  # empty line
                    pass
                # single comment, cloud be character BOM
                elif line.lstrip()[0] == "#" or line.lstrip()[1] == "#":
                    pass
                else:
                    # code line + 1, if it's multiline comment/empty line/single comment
                    lines_count_python += 1
        return lines_count_python
    except Exception as e:
        print(e)
        return 0


def java_c_lines_count(file_path, encoding):  # statistic java or c
    lines_count_java_c = 0
    flag_java = 0
    try:
        with open(file_path, "r", encoding=encoding) as fp:
            for line in fp:
                if line.strip()[:2] == "/*" or line.strip()[-2:] == "*/":  # multiline comment
                    flag_java += 1
                elif flag_java % 2 != 0:
                    continue
                elif line.strip() in string.whitespace:  # empty line
                    pass
                elif line.lstrip()[:2] == "//":  # single comment
                    pass
                else:
                    lines_count_java_c += 1
        return lines_count_java_c
    except Exception as e:
        print(e)
        return 0


def get_files_path(dir_path, queue):  # get file path
    for root, dirs, files in os.walk(dir_path):
        for file in files:  # traverse files of the root directory
            if os.path.splitext(file)[1] in [".py", ".java", ".c"]:  # judge type of file
                file_path = os.path.join(root, file)  # splices absolute path
                queue.put(file_path)  # put in queue


def get_code_lines(queue, total_count_python, total_count_java, total_count_c):  # get code lines
    while not queue.empty():
        file_path = queue.get()
        file_path_suffix = os.path.splitext(file_path)[1]  # get file extension
        if file_path_suffix == ".py":
            try:
                lines_count_python = python_lines_count(file_path, "utf-8")
            except:
                # if error when open file through utf-8
                # or gbk
                lines_count_python = python_lines_count(file_path, "gbk")
            total_count_python.value += lines_count_python
        elif file_path_suffix in [".java", ".c"]:
            lines_count_java_c = java_c_lines_count(
                file_path, "utf-8")
            if file_path_suffix == ".java":
                total_count_java.value += lines_count_java_c
            elif file_path_suffix == ".c":
                total_count_c.value += lines_count_java_c
    return


# multi process and queue, implements code lines count
def get_total_code_lines(dir_path):
    start = time.time()
    queue = multiprocessing.Queue(1000)
    total_count_python = multiprocessing.Value("d", 0)
    total_count_java = multiprocessing.Value("d", 0)
    total_count_c = multiprocessing.Value("d", 0)
    p_get_path = multiprocessing.Process(
        target=get_files_path, args=(dir_path, queue))
    p_get_path.start()
    num_cpu = multiprocessing.cpu_count()
    p_get_lindes = [multiprocessing.Process(target=get_code_lines, args=(queue,
                                                                         total_count_python, total_count_java, total_count_c))
                    for i in range(num_cpu)]
    for p in p_get_lindes:  # start loop thread
        p.start()
        p.join()
    p_get_path.join()

    print("python code lines", int(total_count_python.value))
    print("java code lines", int(total_count_java.value))
    print("c code lines", int(total_count_c.value))
    end = time.time()
    total_time = end - start
    print("Run time is", total_time)
    return int(total_count_python.value), int(total_count_java.value), int(total_count_c.value), total_time


def selectPath():  # Choose directory path
    path_ = filedialog.askdirectory()
    path.set(path_)


def click_submit():  # click button event
    dir_path = path.get()
    total_line_count = get_total_code_lines(dir_path)
    total_count_python.set(str(total_line_count[0]))
    total_count_java.set(str(total_line_count[1]))
    total_count_c.set(str(total_line_count[2]))
    total_time.set("%.3f" % total_line_count[3])


# def get_current_time():
#     current_time = time.strftime(
#         '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     return current_time


# def dynamic_logging(logmsg):
#     global LOG_LINE_NUM
#     current_time = get_current_time()
#     logmsg_in = str(current_time) + ""+str(logmsg)+"\n"


if __name__ == '__main__':
    # instantiation & set params
    windows = Tk()
    windows.title("Code Lines Statistic Tool v1.0")
    windows.geometry("500x360")
    path = StringVar()
    total_count_python = StringVar()
    total_count_java = StringVar()
    total_count_c = StringVar()
    total_time = StringVar()
    logmsg = StringVar()

    ttk.Label(windows, text="Code Lines Statistic Path").grid(
        row=10, column=1, padx=10, pady=10)
    Entry(windows, textvariable=path).grid(row=10, column=2)
    # Create button
    ttk.Button(windows, text="Choose directory", command=selectPath).grid(
        row=10, column=3, padx=10, pady=10)
    ttk.Button(windows, text="Start Statistic", command=click_submit).grid(
        row=20, column=3, padx=10, pady=10)
    # Create Label and Entry
    ttk.Label(windows, text="python code lines:").grid(row=60, column=1)
    Entry(windows, textvariable=total_count_python).grid(row=60, column=2)
    ttk.Label(windows, text="java code lines:").grid(row=70, column=1)
    Entry(windows, textvariable=total_count_java).grid(row=70, column=2)
    ttk.Label(windows, text="C code lines:").grid(row=80, column=1)
    Entry(windows, textvariable=total_count_java).grid(row=80, column=2)
    ttk.Label(windows, text="Run time is(s):").grid(row=90, column=1)
    Entry(windows, textvariable=total_time).grid(row=90, column=2)

    # to do
    # ttk.Label(windows, text="Logger:").grid(row=100, column=1)
    # Entry(windows, textvariable="To od").grid(
    #     row=100, column=2, rowspan=20, ipady=50)

    # initialization
    windows.mainloop()
