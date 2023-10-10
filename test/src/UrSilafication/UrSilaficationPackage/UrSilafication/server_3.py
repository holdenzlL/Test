# Generated by sila2.code_generator; sila2.__version__: 0.10.4

from typing import Optional
from uuid import UUID

from sila2.server import SilaServer

from .feature_implementations.ursilainterface_impl_3 import UrSilaInterfaceImpl
from .generated.ursilainterface import UrSilaInterfaceFeature
from flask.testing import FlaskClient
import socketio


class Server(SilaServer):
    def __init__(self, server_uuid: Optional[UUID] = None):
        # TODO: fill in your server information
        super().__init__(
            server_name="TODO",
            server_type="TODO",
            server_version="0.1",
            server_description="TODO",
            server_vendor_url="https://gitlab.com/SiLA2/sila_python",
            server_uuid=server_uuid,
        )

        self.ursilainterface = UrSilaInterfaceImpl(self)
        self.set_feature_implementation(UrSilaInterfaceFeature, self.ursilainterface)

    def UpdateInvoker(self, invoker):
        self.ursilainterface.UpdateInvoker(invoker)
