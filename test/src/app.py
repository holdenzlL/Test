import time
from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import typer

from multiprocessing import Process
from multiprocessing.managers import BaseManager
from .Invoker.CommandTrigger import CommandTrigger
from .UrSilafication.UrSilaficationPackage.UrSilafication.SilaServer3 import sila_main, UpdateInvoker
from .UrSilafication.UrSilaficationPackage.UrSilafication.feature_implementations.ursilainterface_impl_3 import UrSilaInterfaceImpl

from .StateMachine.UrSm import UrSm
from .Invoker.CommandTrigger import CommandTrigger
from .Commands.Connect import Connect
from .Commands.Disconnect import Disconnect
from .Commands.SendCommand import SendCommand

class SharedEmit():
    def __init__(self):
        self.mEmit=None

    def SetEmit(self, emit: emit):

        self.mEmit = emit

    def GetEmit(self) -> emit:
        return self.mEmit

class SharedInvoker():
    def __init__(self):
        self.mInvoker=None #CommandTrigger(self, None, None, None)

    def SetInvoker(self, invoker: CommandTrigger):

        self.mInvoker = invoker #CommandTrigger(self.mSocket, cmd_connect, cmd_disconnect, cmd_send_command)

    def GetInvoker(self)-> CommandTrigger:
        return self.mInvoker



class CustomSocketIO(SocketIO):
    def __init__(self, *args, **kwargs):
        SocketIO.__init__(self, *args, **kwargs)
        self.mInvoker=None #CommandTrigger(self, None, None, None)
        self.on_event('connect', self.HandleConnection, namespace='/')
        self.mClientId = None
    def SetInvoker(self, invoker: CommandTrigger):
        print(invoker)
        print(self)
        self.mInvoker = invoker
    def GetInvoker(self)-> CommandTrigger:
        return self.mInvoker

    def Run(self, app, host=None, port=None, **kwargs):
        super().run(app=app, host=host, port=port, **kwargs)
        print("Überschrieben RUN Methode öööööööööööööööööööööööööööööö")

    def HandleConnection(self):
        frontend_client_id = request.args.get('clientId')#
        print(f"mClientId={self.mClientId} und Frontend-clientId={frontend_client_id}")
        if self.mClientId is None:
            self.mClientId = frontend_client_id
            local_state_machine = UrSm(self.emit)#socketIO2UI=self)
            cmd_connect = Connect(local_state_machine, name="connection to server command")
            cmd_disconnect = Disconnect(local_state_machine, name="disconnection from server command")
            cmd_send_command = SendCommand(local_state_machine, name="send message to server command")
            invoker = command_trigger = CommandTrigger(self, cmd_connect, cmd_disconnect, cmd_send_command)
            print("******************************************            mSocketIoServer: {}".format(command_trigger))
            Process.run(sila_main(invoker=command_trigger, ip_address="0.0.0.0",
                                port=50052,
                                insecure=False,
                                private_key_file=None,
                                cert_file=None, ca_file_for_discovery=None, server_uuid=None,
                                disable_discovery=False,
                                ca_export_file="ca.pem", debug=False, quiet=False, verbose=False))

        #self.SetInvoker(invoker)
        # shared_object.SetInvoker(invoker)
        #print("-------------------------------------------socketio.SetInvoker(invoker) mit invoker={}".format(invoker))
        #print("-------------------------------------------socketio.GetInvoker() liefert: {}".format(self.GetInvoker()))
        # TODO: alternative hier ein Setter von UrSilafication

app = Flask(__name__)
socketio = CustomSocketIO(app, cors_allowed_origins='*')#, message_queue='redis://localhost:50057')



# custom manager to support custom classes
class CustomManager(BaseManager):
    def __init__(self):
        super(CustomManager, self).__init__()
        # self.mTyper = typer
        self.mInvoker=None
        self.mApp = None #Flask(__name__)
        self.mSocketIO = None #SocketIO(self.mApp, cors_allowed_origins='*')  # , message_queue='redis://localhost:50057')
        #self.mSocketIO.on_event('connect', self.HandleConnection, namespace='/')
        ##self.mApp.route(self.Index, namespace='/')
        #self.mApp.add_url_rule("/", "Index", self.Index)

    def SetInvoker(self, invoker):
        self.mInvoker = invoker

    def SetApp(self, app):
        self.mApp = app

    def SetSocketIO(self, socket):
        self.mSocketIO = socket

    def GetAll(self):
        return {"socketIO": self.mApp, "socketIO": self.mSocketIO, "invoker": self.mInvoker}

    def GetApp(self) -> Flask:
        return self.mApp

    def GetSocketIO(self):
        return self.mSocketIO

    def GetInvoker(self):
        return self.mInvoker

    def Print(self):
        print("invoker:{}, socketIO:{}".format(self.mInvoker, self.mSocketIO))



    #def HandleConnection(self):
    #    from .StateMachine.UrSm import UrSm
    #    from .Invoker.CommandTrigger import CommandTrigger
    #    from .Commands.Connect import Connect
    #    from .Commands.Disconnect import Disconnect
    #    from .Commands.SendCommand import SendCommand
    #    local_state_machine = UrSm(socketIO2UI=self.GetSocketIO())
    #    cmd_connect = Connect(local_state_machine, name="connection to server command")
    #    cmd_disconnect = Disconnect(local_state_machine, name="disconnection from server command")
    #    cmd_send_command = SendCommand(local_state_machine, name="send message to server command")
    #
    #    self.SetInvoker(CommandTrigger(self.mSocketIO, cmd_connect, cmd_disconnect, cmd_send_command))

    def Index(self):
       #template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
       return render_template('index.html')#template_path)

    def IsIvokerInitialized(self):
        ret_val=False
        if self.mInvoker is not None:
            ret_val=True
        return ret_val


    def PrintOut(self):
        self.Print()

    #def app_process_methode(self, lock):
    #    with lock:
    #        socket = self.GetSocketIO()
    #        app = self.GetApp()
    #        lock.release()
    #        print("----- APP run wird ausgeführt")
    #        socket.run(app, host='0.0.0.0', port=50057, allow_unsafe_werkzeug=True, debug=True,
    #                   use_reloader=False)
        #while True:
        #    if lock.acquire():
        #        try:
        #            socket = self.GetSocketIO()
        #            app = self.GetApp()
        #            print("----- APP run wird ausgeführt")
        #            lock.release()
        #            socket.run(app, host='0.0.0.0', port=50057, allow_unsafe_werkzeug=True, debug=True,
        #                       use_reloader=False)
        #        finally:
        #            lock.release()
        #    else:
        #        print(
        #            "--------------------------------APP PROZESS: ES WIRD GEWARTET BIS SHARED OBJECT WIEDER ZUGÄNGLICH IST---------------")
        #        time.sleep(0.5)



def initialize_emit_mechanism(queue_obj):
    print("----- initialize_emit_mechanism wird ausgeführt, Verwendeter socketio={}".format(socketio))
    print("----- initialize_emit_mechanism wird ausgeführt, Verwendeter socketio.emit={}".format(socketio.emit))
    item = queue_obj.get()
    item.SetEmit(socketio.emit)
    queue_obj.put(item)
    time.sleep(0.5)

def initialize_invoker_mechanism(queue_obj):
    print("----- initialize_invoker_mechanism wird ausgeführt, Verwendeter socketio={}".format(socketio))
    shared_object = queue_obj.get()
    local_state_machine = UrSm(emit=socketio.emit)#socketIO2UI=socketio)
    cmd_connect = Connect(local_state_machine, name = "connection to server command")
    cmd_disconnect = Disconnect(local_state_machine, name = "disconnection from server command")
    cmd_send_command = SendCommand(local_state_machine, name = "send message to server command")
    invoker = CommandTrigger(socketio, cmd_connect, cmd_disconnect, cmd_send_command)
    shared_object.SetInvoker(invoker)
    print("-----initialize_invoker_mechanism shared_object={}".format(shared_object))
    print("-----initialize_invoker_mechanism shared_object.GetInvoker()={}".format(shared_object.GetInvoker()))
    queue_obj.put(shared_object)
    time.sleep(0.5)

@app.route('/')
def index():
    #template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    return render_template('index.html')#template_path)


@app.before_request
def your_function():
    print("execute before server starts &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(socketio)