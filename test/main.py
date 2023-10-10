import multiprocessing

from src.app import CustomManager
from src.app import app, socketio
from src.app import CustomSocketIO
from src.app import SharedInvoker
from src.app import SharedEmit
from src.app import initialize_invoker_mechanism
from src.app import initialize_emit_mechanism


from multiprocessing import Process, Manager, Lock, Queue

import time
from flask_socketio import SocketIO
import typer
from src.UrSilafication.UrSilaficationPackage.UrSilafication.SilaServer3 import sila_main
from src.Invoker.CommandTrigger import CommandTrigger

def app_process_methode(queue_obj):
    #print("----- APP run wird ausgeführt, Verwendeter socketio={}".format(socketio))
    #shared_object=queue_obj.get()
    #print("----- APP shared object={}".format(shared_object))
    ##print("----- APP shared invoker={}".format(shared_object.GetInvoker()))
    #queue_obj.put(shared_object)
    #queue_obj.put(socketio.emit)

    socketio.run(app, host='0.0.0.0', port=50057, allow_unsafe_werkzeug=True, debug=True, use_reloader=False)

def sila_process_methode(queue_obj):
    #item = queue_obj.get()
    #print(item)
    emit = socketio.emit #item.mEmit #invoker = shared_object.GetInvoker()
    print(emit)
    print(socketio)  
    typer.run(sila_main(invoker=socketio, ip_address="0.0.0.0",
                                     port=50052,
                                     insecure=False,
                                     private_key_file=None,
                                     cert_file=None, ca_file_for_discovery=None, server_uuid=None,
                                     disable_discovery=False,
                                     ca_export_file="ca.pem", debug=False, quiet=False, verbose=False))

if __name__ == "__main__":

    queue_obj = multiprocessing.Queue(maxsize=103000048)
    # create a shared set instance

    shared_object = SharedEmit() #SharedInvoker() #CustomSocketIO()
    print("original shared_object: {}".format(shared_object))


    app_process = Process(target=app_process_methode, args=(queue_obj,))
    #print_process = Process(target=initialize_invoker_mechanism, args=(queue_obj,))
    #print_process = Process(target=initialize_emit_mechanism, args=(queue_obj,))
    sila_process = Process(target=sila_process_methode, args=(queue_obj,))

    print("#################################################################################")
    print("----------------------------- run app server -----------------------------------")
    print("#################################################################################")
    # start some child processes
    app_process.start()
    time.sleep(5)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("----------------------------- run check methode -----------------------------------")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #shared_object.SetEmit(socketio.emit)
    #queue_obj.put(shared_object)
    #print_process.start()
    #print_process.join()


    print("---------------------------------------------------------------------------------")
    print("----------------------------- run sila server -----------------------------------")
    print("---------------------------------------------------------------------------------")
    #sila_process.start()
    app_process.join()
    #sila_process.join()

