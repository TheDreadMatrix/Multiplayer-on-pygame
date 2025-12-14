import asyncio
import pygame as pg
import json



class UPDClient(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.running = True
        self.players = []

        self.exc = None
        self.x = 0
        self.y = 0


    def error_received(self, exc):
        self.running = False
        self.exc = exc


    def connection_lost(self, exc):
        print(f"Client get lost {exc}")

    def connection_made(self, transport):
        self.transport = transport


    def datagram_received(self, data, addr):
        json_response = json.loads(data.decode())

        
        self.x = json_response["x"]
        self.y = json_response["y"]
        self.players = json_response["players"]
        

    def send_action(self, action: dict):
        if self.transport:
            self.transport.sendto(action.encode())



async def load_game(protocol):
    pg.init()
    screen = pg.display.set_mode((800, 600))
   


    is_run = True
    clock = pg.time.Clock()
    actions = {}
    while is_run:
        screen.fill((255, 255, 255))
        keys = pg.key.get_pressed()
        pg.display.set_caption(f"FPS: {clock.get_fps()}")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    is_run = False
            if not protocol.running:
                pg.display.message_box("Error", f"Error as {protocol.exc}")
                is_run = False
        

        if keys[pg.K_d]:
            actions["dir-x"] = "right"
        elif keys[pg.K_a]:
            actions["dir-x"] = "left"
        else:
            actions["dir-x"] = "stop-x"
        
        

        if keys[pg.K_w]:
            actions["dir-y"] = "up"
        elif keys[pg.K_s]:
            actions["dir-y"] = "down"
        else:
            actions["dir-y"] = "stop-y"
       
       
        protocol.send_action(json.dumps(actions))


        for player in protocol.players:
            pg.draw.rect(screen, (255, 0, 0), (round(player["x"]), round(player["y"]), 100, 100), width=3)

        pg.draw.rect(screen, (255, 0, 0), (round(protocol.x), round(protocol.y), 100, 100), width=3)

        pg.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pg.quit()



async def main():
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UPDClient(),
        remote_addr=("127.0.0.1", 6060)
    )

    try:
        await load_game(protocol)
    finally:
        transport.close()




asyncio.run(main())