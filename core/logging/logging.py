import json

#ANSI
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"

BOLD_RED = "\033[1;31m"
BOLD_GREEN = "\033[1;32m"
BOLD_BLUE = "\033[1;34m"
#ANSI

def load_error(add:str):
    with open(add, "r", encoding="utf-8") as f:
        error_data = json.load(f)
    return error_data

add = "./error_lists.json"


def error_raiser(error_name:str,error_dict):
    error_id = error_dict[error_name]["id"]
    print(f"{error_id}")
    pass


if __name__ == "__main__":
    error_name = input("please input the name of error:")
    error_dict = load_error(add)
    error_raiser(error_name,error_dict)

class error_log:
    def __init__(self):
        #
        pass
    def generate(self,add:str):
        #
        pass

    def write(self):
        pass

    #...
    pass

#1.控制台日志各一份

#2.ANSI转义字符去写颜色

#3.格式[类型][id][系统消息][注释...]
