async_mode = None  # "eventlet"

import eventlet

eventlet.monkey_patch(socket=True, thread=True, time=True)

# if async_mode == "eventlet":
#     import eventlet

#     eventlet.monkey_patch()
# elif async_mode == "gevent":
#     from gevent import monkey

#     monkey.patch_all()


import time
import threading
from flask import Flask, request, jsonify, copy_current_request_context
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS

from ibapi.contract import Contract
from ibapp import IBAPP


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
# CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    logger=True,
    engineio_logger=True,
    cors_allowed_origins=["http://localhost:8000", "http://localhost:5001"],
    async_mode=async_mode,
)
# socketio = SocketIO(app)


@app.route("/")
def index():
    return "Hello world!!"


@socketio.event
def connect(auth):
    print("connected")
    print(request.sid, auth)

    emit("connected", {"data": "Connected"})


@socketio.event
def get_data():
    print("get_data")
    emit("get_data_received", "get_data")

    def start_app():
        ibapp = IBAPP(socketio=socketio)
        ibapp.connect_tws()

        # @copy_current_request_context
        def run_loop():
            ibapp.run()

        # with app.test_request_context():
        # thread = threading.Thread(target=run_loop, daemon=True)
        # thread.start()
        thread = socketio.start_background_task(target=run_loop)
        # thread.join()
        # time.sleep(1)

        print("requesting data")
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        ibapp.reqMktData(1, contract, "", False, False, [])
        print("requested data")
        # time.sleep(10)
        # ibapp.disconnect()
        print("-" * 60)
        print("ibapp disconnected")
        print("-" * 60)

    # thread = socketio.start_background_task(target=start_app)
    start_app()


@socketio.event
def disconnect():
    print("user disconnected")


mock_intraday_high = {
    "time": "09:30:00",
    "symbol": "AAPL",
    "price": 100.00,
    "gap": 0.00,
    "cnt": 0,
}


def intraday_high():
    socketio.emit("intraday_high", mock_intraday_high)


def intraday_low():
    socketio.emit("intraday_low", mock_intraday_high)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
