import asyncio
import pygame as pg
import json
import time


class UPDServer(asyncio.DatagramProtocol):
    def __init__(self):
       self.players = {}
       self.transport = None

    def datagram_received(self, data, addr):
        message = json.loads(data.decode())
        print(message)

        if addr not in self.players:
            self.players[addr] = {"x": 0, "y": 0, "dx":0, "dy":0}

        player = self.players[addr]
        print(self.players[addr], addr)

 
        if message["dir-x"] == "right":
            player["dx"] = 200  
        elif message["dir-x"] == "left":
            player["dx"] = -200
        elif message["dir-x"] == "stop-x":
            player["dx"] = 0
        


        if message["dir-y"] == "up":
            player["dy"] = -200
        elif message["dir-y"] == "down":
            player["dy"] = 200
        elif message["dir-y"] == "stop-y":
            player["dy"] = 0
        

    async def game_loop(self):
        last_time = time.time()
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            
            for addr, p in self.players.items():
                p["x"] += p["dx"] * dt
                p["y"] += p["dy"] * dt

                
                self.transport.sendto(json.dumps({"x": p["x"], "y": p["y"]}).encode(), addr)
                #self.transport.sendto(json.dumps(self.players).encode())

            await asyncio.sleep(1/60)


    def error_received(self, exc):
        print(f"Error as {exc}")


    def connection_made(self, transport):
        self.transport = transport
        print("Server started")


    def connection_lost(self, exc):
        print("Server stopped")

       



async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UPDServer(),
        local_addr=("127.0.0.1", 6060)
    )

    try:
        await protocol.game_loop()
    finally:
        transport.close()




try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("done")