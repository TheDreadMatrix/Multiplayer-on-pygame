import asyncio
import pygame as pg
import json



class UPDClient(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.running = True
        self.players = []

        self.exc = None
        self.addr = []
        self.x = 0
        self.y = 0
        self.name = ""
        self.message = ""


    def error_received(self, exc):
        self.running = False
        self.exc = exc


    def connection_lost(self, exc):
        print(f"Client get lost {exc}")

    def connection_made(self, transport):
        self.transport = transport
        self.addr = transport.get_extra_info("sockname")

        print(f"My client address is {self.addr}")


    def datagram_received(self, data, addr):
        json_response = json.loads(data.decode())

        #наши данные
        self.x = json_response["you"]["x"]
        self.y = json_response["you"]["y"]
        self.name = json_response["you"]["name"]

        #данные о игроках всех
        self.players = json_response["players"]
        

    def send_action(self, action: dict):
        if self.transport:
            self.transport.sendto(action.encode())



async def load_game(protocol):
    pg.init()
    screen = pg.display.set_mode((800, 600))
   
    font = pg.font.Font(None, 25)
    

    is_run = True
    clock = pg.time.Clock()
    actions = {"type": "connected"}
    while is_run:
        screen.fill((255, 255, 255))
        keys = pg.key.get_pressed()
        pg.display.set_caption(f"FPS: {int(clock.get_fps())}")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_run = False
                actions["type"] = "disconnect"
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    is_run = False
                    actions["type"] = "disconnect"
            if not protocol.running:
                pg.display.message_box("Error", f"Error as {protocol.exc}")
                is_run = False
                actions["type"] = "disconnect"
        

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
            if player["name"] != protocol.name:
                pg.draw.rect(screen, (255, 0, 0), (round(player["x"]), round(player["y"]), 100, 100), width=3)
                screen.blit(font.render(f"Name: {player["name"]}", True, (0, 0, 0)), (round(player["x"]), round(player["y"] - 12)))



        pg.draw.rect(screen, (255, 0, 0), (round(protocol.x), round(protocol.y), 100, 100), width=3)
        name_text = font.render(f"Name: {protocol.name}", True, (0, 0, 0))
        screen.blit(name_text, (round(protocol.x), round(protocol.y - 12)))

        screen.blit(font.render(f"Players count: {len(protocol.players)}", True, (0, 0, 0)), (100, 100))

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