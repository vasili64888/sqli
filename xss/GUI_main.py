from tkinter import *
import threading
import os ,sys
from XSSer import XSSer

if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x\n")
    sys.exit(1)

TITLE = "XSSer"
SUBTITLE = "(XSS scanner)"
LABELS = {
    "domain_lbl":       "Domain to scan:",
    "options_title_lbl": "Options:",
    "quick_scan_lbl":   "Quick scan",
    "shallow_scan_lbl": "Shallow scan",
    "submit_btn":       "Scan"
}
LABELS_CN={
    "domain_lbl":       "域名:",
    "options_title_lbl": "选项:",
    "quick_scan_lbl":   "快速扫描",
    "shallow_scan_lbl": "浅扫描",
    "submit_btn":       "扫描"
}
FONT = "Helvetica"
PWD=os.getcwd()
INPUTS_NAME = PWD+"\\example\\XSSer-master\\crafted_inp.txt"
UNMATCHING_DOMAIN_ERR = "Oops: It seems like the domain you specified is not in the expected format:\nhttp://yourdomain.com"
NO_ERRORS_STR = "No errors."


class GUI(Frame):

    def __init__(self, root):  
        Frame.__init__(self, root)
        self.parent = root
        self.quick_scan = BooleanVar()#是否快速扫描 选择框
        self.domain = StringVar()#域名输入框
        self.errors = StringVar(value=NO_ERRORS_STR)#错误信息
        self._next_row = 6
        self.inps = self.get_inputs_list()#获取输入框列表
        self.init_ui()

    def init_ui(self):
        self.parent.title(TITLE)#标题
        self.pack(fill=BOTH, expand=1)#flll=BOTH是填充整个窗口，expand=1是允许窗口扩展
        #self.style = Style()
        #self.style.theme_use("default")

        # Titles and subtitles
        title = Label(self, text=TITLE, font=(FONT, 36))
        title.grid(row=0, columnspan=3, pady=(20, 0), padx=20)
        subtitle = Label(self, text=SUBTITLE, font=(FONT, 10))
        subtitle.grid(row=1, columnspan=3, pady=(0, 13))

        # Form
        # Domain
        domain_label = Label(self, text=LABELS["domain_lbl"], font=(FONT, 11))
        domain_label.grid(row=2, sticky=E, padx=(20, 10))
        domain_input = Entry(self, width=75, textvariable=self.domain)
        domain_input.grid(row=2, column=1, padx=(0, 20), sticky=W)

        #defult domain
        domain_input.insert(0, "http://localhost/p/vul/xss/xss_01.php")
        # Options
        options_label = Label(self, text=LABELS["options_title_lbl"],font=(FONT, 11))
        options_label.grid(row=3, sticky=E)
        quick_scan_checkbox = Checkbutton(self, text=LABELS["quick_scan_lbl"],font=(FONT, 9),variable=self.quick_scan)
        quick_scan_checkbox.grid(row=3, column=1, sticky=W)

        # Submit
        submit_btn = Button(self, text=LABELS["submit_btn"],command=self.on_click)
        submit_btn.grid(row=4, columnspan=3, pady=10)

        # Errors
        errors_lbl = Label(self, textvariable=self.errors, font=(FONT, 11),fg="red")#fg是字体颜色
        errors_lbl.grid(row=5, columnspan=2, padx=20, pady=(10, 25), sticky=W)

    def on_click(self):
        if not self.valid_domain():#非法域名
            self.errors.set(UNMATCHING_DOMAIN_ERR)
            return
        else:#合法域名
            self.errors.set(NO_ERRORS_STR)
            self.init_scan()

    def valid_domain(self):
        """
        Checks if the domain is valid ?
        :return: True/False, indicating whether the submitted domain is valid
        """
        url = self.domain.get()#获取输入域名
        return url.startswith("http://") 
            #or url.startswith("https://")) and #url.find(".") != -1 and url[-1] != '.' and url.find(" ") == -1

    def init_scan(self):
        title = Label(self, text=self.domain.get(), font=(FONT, 11))#扫描结果标题
        title.grid(row=self._next_row, sticky=N)

        scrollbar = Scrollbar(self)
        scrollbar.grid(row=self._next_row+1, column=2, sticky=NSEW)#滚动条style

        status_box = Listbox(self, yscrollcommand=scrollbar.set)
        status_box.grid(row=self._next_row+1, column=1, padx=(0, 20),sticky=NSEW)

        scanner = XSSer(self.domain.get(), self.inps, self.quick_scan.get(),status_box)

        collapse_btn = Button(self, text="Toggle Log",command=scanner.toggle_log)
        collapse_btn.grid(row=self._next_row, column=1)

        self._next_row += 2

        #threading.start_new_thread(scanner.scan, ())
        threading.Thread(target=scanner.scan).start()

    def get_inputs_list(self):
        """
        Reads the inputs from their file and returns them as a list
        :return: The inputs list
        """
        ret = ""
        with open(INPUTS_NAME, "rt") as inps_f:
            ret = inps_f.read().split("\n")
        return ret[:-1]  # To remove the space in the end


def center(root):# Center the window GUI
    root.update_idletasks()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    root.geometry("%dx%d+%d+%d" % (size + (x, y)))


root = Tk()
# root.resizable(0,0)  # Disable resizing
ex = GUI(root)
center(root)

root.mainloop()
