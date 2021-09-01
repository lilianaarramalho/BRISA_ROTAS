class sublanco(object):

    def __init__(self,id,nome,id_co):
        self.id=id
        self.nome=nome
        self.lista_nos=[]
        self.id_co=id_co

    def __repr__(self):
        return str(self.nome)


class no(object):

    def __init__(self, id, nome,pausa,almoco,vistoria,co,espera):
        self.id = id
        self.nome = nome
        self.pausa=pausa
        self.almoco=almoco
        self.vistoria=vistoria
        self.co=co #se for um nó tipo portagem (que só existe por causa dos almoços) não precisa de ser verificado
        self.distancias=[]
        self.espera=espera

    def __repr__(self):
        return str(self.nome)

class co(object):

    def __init__(self,id,nome):
        self.id = id
        self.nome = nome
        self.lista_sublancos = []
        self.id_no=[]

    def __repr__(self):
        return str(self.nome)

class turno(object):

    def __init__(self,id,inicio,pausa,almoco,fim):
        self.id=id
        self.inicio=inicio
        self.pausa=pausa
        self.almoco=almoco
        self.fim=fim

    def __repr__(self):
        return str(self.inicio)

