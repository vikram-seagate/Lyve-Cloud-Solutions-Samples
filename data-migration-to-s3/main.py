from tkinter import *
from time import sleep
import multiprocessing.dummy as mp
import threading


def count_to_10(i):
    # for i in range(1, 11):
    sleep(0.5)
    print(i)
    counter_label.configure(text=i)  # Update the text in "Label" widget.
    root.update()  # Let root update the main window.


def GUI():
    global root
    root = Tk()

    run_button = Button(root, text="run", command=count_to_10)
    run_button.pack()

    global counter_label
    counter_label = Label(root, text="counter")
    counter_label.pack()

    t1 = threading.Thread(target=count_to_10)
    t1.setDaemon(True)
    t1.start()
    t2 = threading.Thread(target=count_to_10)
    t2.setDaemon(True)
    t2.start()
    # p = mp.Pool(4)
    # p.daemon = True
    # p.map(count_to_10, range(1, 11))

    # p.close()
    # p.join()
    root.mainloop()


GUI()
