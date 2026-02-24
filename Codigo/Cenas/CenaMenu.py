import pygame

def TelaMenu(TELA, ESTADOS, CONFIG, INFO, Parametros):
    pass

def InicializaMenu(TELA, ESTADOS, CONFIG, INFO):

    return {
        "TelaAtiva": TelaMenu
    }

def MenuLoop(TELA, RELOGIO, ESTADOS, CONFIG, INFO):

    Parametros = InicializaMenu(TELA, ESTADOS, CONFIG, INFO)

    while ESTADOS["Inicio"]:
        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                ESTADOS["Inicio"] = False
                ESTADOS["Rodando"] = False
                return
        
        Parametros["TelaAtiva"](TELA, ESTADOS, CONFIG, INFO, Parametros)
        
        pygame.display.update() 
        RELOGIO.tick(CONFIG["FPS"])