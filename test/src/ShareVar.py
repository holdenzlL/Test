
def initialize():
    global g_invoker
    g_invoker = None

def set_g_invoker(val):
    print("------------------------------------------------------------------------------------ new set of invoker:{}".format(val))
    g_invoker = val

def get_g_invoker():
    return g_invoker