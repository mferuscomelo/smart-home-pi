# Adapted from: https://github.com/Ladvien/arduino_ble_sense
# IMPORTANT: Use PowerShell instead of WSL to connect with BLE

# sudo usermod -a -G bluetooth pi
# sudo systemctl daemon-reload
# sudo systemctl restart bluetooth

import os
import sys
import asyncio
import pyrebase
import platform
import bluetooth
from datetime import datetime
from typing import Callable, Any, List
from time import sleep

from aioconsole import ainput
from bleak import BleakClient, discover

class Database:

    def __init__(self):
        firebase_config = {
            "apiKey": "AIzaSyAKf_7vnJNeeGfnrS99RvZ-WaE4ge68JFM",
            "authDomain": "smart-home-7c688.firebaseapp.com",
            "databaseURL": "https://smart-home-7c688-default-rtdb.firebaseio.com",
            "storageBucket": "smart-home-7c688.appspot.com"
        }

        firebase = pyrebase.initialize_app(firebase_config)
        self.db = firebase.database()

    def writeToDB(self, name: str, value: str):
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        data = {
            "timestamp": timestamp,
            "message": value
        }
        self.db.child(name).push(data)

class Connection:

    client: BleakClient = None

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        read_characteristic: str,
        write_characteristic: str,
        data_dump_handler: Callable[[str, str], None]
    ):
        self.loop = loop
        self.read_characteristic = read_characteristic
        self.write_characteristic = write_characteristic
        self.data_dump_handler = data_dump_handler

        self.connected = False
        self.connected_device = None

    def on_disconnect(self, client: BleakClient):
        self.connected = False
        # Put code here to handle what happens on disconnect.
        print(f"Disconnected from {self.connected_device.name}!")

    async def cleanup(self):
        if self.client:
            await self.client.stop_notify(read_characteristic)
            await self.client.disconnect()

    async def manager(self):
        print("Starting connection manager.")
        while True:
            if self.client:
                await self.connect()
            else:
                await self.select_device()
                await asyncio.sleep(15.0)

    async def connect(self):
        if self.connected:
            return
        try:
            await self.client.connect()
            self.connected = self.client.is_connected
            if self.connected:
                print(F"Connected to {self.connected_device.name}")
                self.client.set_disconnected_callback(self.on_disconnect)
                await self.client.start_notify(
                    self.read_characteristic, self.notification_handler,
                )
                while True:
                    if not self.connected:
                        break
                    await asyncio.sleep(3.0)
            else:
                print(f"Failed to connect to {self.connected_device.name}")
        except Exception as e:
            print(e)

    async def select_device(self):
        print("Bluetooh LE hardware warming up...")
        await asyncio.sleep(2.0)  # Wait for BLE to initialize.
        devices = await discover()

        print("Please select device: ")
        for i, device in enumerate(devices):
            print(f"{i}: {device.name}")

        response = -1
        while True:
            response = await ainput("Select device: ")
            try:
                response = int(response.strip())
            except:
                print("Please make valid selection.")

            if response > -1 and response < len(devices):
                break
            else:
                print("Please make valid selection.")

        print(f"Connecting to {devices[response].name}")
        self.connected_device = devices[response]
        self.client = BleakClient(devices[response].address, loop=self.loop)

    async def notification_handler(self, sender: str, data_bytes: bytearray):
        data = data_bytes.decode()
        category = data.split(":")[0]
        value = data.split(":")[1][1:]

        if("Door" in value):
            if(not is_home):
                self.data_dump_handler(category, value)
        else:
            self.data_dump_handler(category, value)

async def checkIfHome(is_currently_home):
    await asyncio.sleep(2)
    if(bluetooth.lookup_name("BC:A5:8B:34:07:FF") == "Milan's Note 9" and is_currently_home == False):
        connection.data_dump_handler("notifications", "Status changed to Home")
        return True
    elif(bluetooth.lookup_name("BC:A5:8B:34:07:FF") != "Milan's Note 9" and is_currently_home == True):
        connection.data_dump_handler("notifications", "Status changed to Away")
        return False
    else:
        return is_currently_home

#############
# Loops
#############
async def user_console_manager(connection: Connection):
    if connection.client and connection.connected:
        input_str = await ainput("Enter command: ")
            
        bytes_to_send = bytearray(map(ord, input_str))
        await connection.client.write_gatt_char(write_characteristic, bytes_to_send)
    else:
        await asyncio.sleep(2.0)


async def main():
    while True:
        global is_home
        is_home = await checkIfHome(is_home)
        await asyncio.sleep(5)


#############
# App Main
#############
read_characteristic = "00001143-0000-1000-8000-00805f9b34fb"
write_characteristic = "00001142-0000-1000-8000-00805f9b34fb"
is_home = True

if __name__ == "__main__":

    # Create the event loop.
    loop = asyncio.get_event_loop()

    db = Database()
    connection = Connection(
        loop, read_characteristic, write_characteristic, db.writeToDB
    )
    try:
        asyncio.ensure_future(connection.manager())
        asyncio.ensure_future(user_console_manager(connection))
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print()
        print("User stopped program.")
    finally:
        print("Disconnecting...")
        loop.run_until_complete(connection.cleanup())
        exit()