import asyncio
import pygame as pg
import json
import time


class UPDServer(asyncio.DatagramProtocol):
    def __init__(self):
       self.players = {}
       self.transport = None
       self.count = 0

    def datagram_received(self, data, addr):
        message = json.loads(data.decode())
        print(message)

        if addr not in self.players:
            self.count += 1
            self.players[addr] = {"x": 0, "y": 0, "dx":0, "dy":0, "name": f"чувак {self.count}"}

        if message["type"] == "disconnect":
            del self.players[addr]
            return

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
        idle_time = 0
        IDLE_TIMEOUT = 60
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            if not self.players:
                idle_time += dt
                if idle_time > IDLE_TIMEOUT:
                    print("No players for 1 min, stopping server")
                    break
            else:
                idle_time = 0

            
            snapshot = list(self.players.items())

            #Здесь писал мне оптимизацию Chat GPT признаюсь...
            for _, p in snapshot:
                p["x"] += p.get("dx", 0) * dt
                p["y"] += p.get("dy", 0) * dt

           
            all_players = []
            for addr, p in snapshot:
                all_players.append({
                    "ip": addr[0],
                    "port": addr[1],
                    "name": p.get("name", "ernar"),
                    "x": p.get("x", 0),
                    "y": p.get("y", 0)
                })

            
            for addr, p in snapshot:
                payload = {
                    "you": {
                        "x": p.get("x", 0),
                        "y": p.get("y", 0),
                        "name": p.get("name", "ернар")
                    },
                    "players": all_players
                }

                try:
                    self.transport.sendto(
                        json.dumps(payload).encode(),
                        addr
                    )
                except Exception as e:
                    print("send error:", e)
    
             
                

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