import random
import logging
from queue import Queue
import matplotlib.pyplot as plt

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Atendente:
    def __init__(self, tipo, id):
        self.tipo = tipo  
        self.id = id
        self.ocupado = False

    def atender(self):
        self.ocupado = True

    def liberar(self):
        self.ocupado = False

class Servidor:
    def __init__(self, id, capacidade):
        self.id = id
        self.capacidade = capacidade
        self.atendentes = []
        self.ativo = True  
        self.atendimentos = 0

    def adicionar_atendente(self, atendente):
        self.atendentes.append(atendente)

    def remover_atendente(self, atendente_id):
        self.atendentes = [a for a in self.atendentes if a.id != atendente_id]

    def status(self):
        livres = len([a for a in self.atendentes if not a.ocupado])
        return {"id": self.id, "livres": livres, "capacidade": self.capacidade, "ativo": self.ativo}

    def processar(self, tipo, fila):
        if not self.ativo or fila.empty():
            return
        while not fila.empty() and self.status()["livres"] > 0:
            fila.get()
            self.atendimentos += 1
            logging.info(f"Servidor {self.id} processou uma solicitação de {tipo.capitalize()}.")

    def falhar(self):
        self.ativo = False

    def recuperar(self):
        self.ativo = True

# Configuracao inicial
servidores = [
    Servidor("A", 5),
    Servidor("B", 7),
    Servidor("C", 10)
]

# Adiciona atendentes aos servidores
tipos = ['suporte', 'vendas']
for servidor in servidores:
    for _ in range(servidor.capacidade):
        tipo = random.choice(tipos)
        servidor.adicionar_atendente(Atendente(tipo, id=random.randint(1, 1000)))


fila_suporte = Queue(maxsize=50)
fila_vendas = Queue(maxsize=50)


historico_falhas = {servidor.id: 0 for servidor in servidores}
historico_atendimentos = []
redirecionamentos = 0


timesteps = 100
for t in range(timesteps):
    logging.info(f"Timesteps {t + 1}/{timesteps}")

    # Gerar solicitações
    num_requisicoes = random.randint(10, 20)
    for _ in range(num_requisicoes):
        tipo = random.choice(tipos)
        if tipo == 'suporte' and not fila_suporte.full():
            fila_suporte.put(f"Solicitação Suporte {t}")
        elif tipo == 'vendas' and not fila_vendas.full():
            fila_vendas.put(f"Solicitação Vendas {t}")
        elif fila_suporte.full() or fila_vendas.full():
            logging.warning("Buffer de solicitações cheio! Simulação encerrada com falha.")
            exit()

    #
    for servidor in servidores:
        if random.random() < 0.1: 
            servidor.falhar()
            historico_falhas[servidor.id] += 1
            logging.warning(f"Servidor {servidor.id} falhou!")

    
    atendimentos_por_timestep = 0
    for servidor in servidores:
        if servidor.ativo:
            servidor.processar("suporte", fila_suporte)
            servidor.processar("vendas", fila_vendas)
            atendimentos_por_timestep += servidor.atendimentos
        else:
            redirecionamentos += fila_suporte.qsize() + fila_vendas.qsize()

    historico_atendimentos.append(atendimentos_por_timestep)

    
    for servidor in servidores:
        if not servidor.ativo and random.random() < 0.2: 
            servidor.recuperar()
            logging.info(f"Servidor {servidor.id} recuperado!")

    
    if random.random() < 0.1:  
        servidor_ajustado = random.choice(servidores)
        if random.random() < 0.5 and servidor_ajustado.atendentes:  
            servidor_ajustado.atendentes.pop()
            logging.info(f"Servidor {servidor_ajustado.id} perdeu um atendente.")
        else:  
            novo_atendente = Atendente(random.choice(tipos), id=random.randint(1000, 2000))
            servidor_ajustado.adicionar_atendente(novo_atendente)
            logging.info(f"Servidor {servidor_ajustado.id} ganhou um novo atendente.")

# Gráficos de desempenho
plt.figure(figsize=(12, 6))

# Gráfico 1: Atendimentos por timestep
plt.subplot(1, 3, 1)
plt.plot(historico_atendimentos, label="Atendimentos")
plt.title("Atendimentos por Timestep")
plt.xlabel("Timestep")
plt.ylabel("Atendimentos")
plt.legend()

# Gráfico 2: Falhas por servidor
plt.subplot(1, 3, 2)
plt.bar(historico_falhas.keys(), historico_falhas.values(), color="orange")
plt.title("Falhas por Servidor")
plt.xlabel("Servidores")
plt.ylabel("Número de Falhas")

# Gráfico 3: Redirecionamentos
plt.subplot(1, 3, 3)
plt.pie([redirecionamentos, sum(historico_atendimentos)], labels=["Redirecionados", "Atendidos"], autopct="%1.1f%%")
plt.title("Distribuição de Solicitações")

plt.tight_layout()
plt.show()
