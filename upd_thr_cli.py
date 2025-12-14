import socket
import threading
import json
import pygame as pg

class Client:
    def __init__(self, host: str, port: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.running = True
        self.client.settimeout(0.5)

        self.rect = pg.FRect(0, 0, 100, 100)

    def run(self):
        while self.running:
            try:
                data, addr = self.client.recvfrom(1024)
                data_decoded = json.loads(data.decode())

                self.rect.x = data_decoded["x"]
                self.rect.y = data_decoded["y"]

                print("Ответ:", data.decode(), addr)
                
            except socket.timeout:
                continue 
            except Exception as e:
                print("sorry", e)
                self.running = False

        self.client.close()

    def send(self, text: str):
        self.client.sendto(text.encode(), (self.host, self.port))


class Game:
    def __init__(self, client: Client):
        self.client = client
        self.is_run = True

        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        self.clock = pg.time.Clock()
        self.player = pg.Rect(100, 200, 100, 100)

    def run(self):
        while self.is_run:
            pg.display.set_caption(f"FPS: {self.clock.get_fps()}")
            keys = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.is_run = False
                    self.client.running = False

            
            

            
            if keys[pg.K_w]:
                self.client.send("up")
            elif keys[pg.K_s]:
                self.client.send("down")
            else:
                self.client.send("none-y")


            if keys[pg.K_d]:
                self.client.send("right")
            elif keys[pg.K_a]:
                self.client.send("left")
            else:
                self.client.send("none-x")


            self.screen.fill((255, 255, 255))
            pg.draw.rect(self.screen, (255, 0, 0), self.client.rect, width=3)
            pg.display.flip()

            self.clock.tick(60)

        pg.quit()


client = Client("127.0.0.1", 6060)
game = Game(client)

client_thr = threading.Thread(target=client.run, daemon=True)
client_thr.start()

game.run()
