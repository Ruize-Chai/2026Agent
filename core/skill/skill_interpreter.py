from notes import note
from typing import Any,Dict,List

def work_flow_list(work_flow:List):
    res = []
    for notes in work_flow:
        notes_object = None#
        res.append(notes_object)
        pass
    return res

def work_flow_context(work_flow:List):
    pass

def flow_go(work_flow:List):
    lists  = work_flow_list(work_flow)
    contexts = work_flow_context(work_flow)
    note_flow = 0
    while(True):
        note_flow = lists[note_flow].execute(lists,contexts)
        if note_flow == None:
            break
    pass