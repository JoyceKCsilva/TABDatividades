import pymongo
import random
import time
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)

CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
DB = CLIENT["iot_factory_db"]

def simulate_real_time_data():
    # 1. Recuperar IDs de todos os sensores existentes
    devices = list(DB["devices"].find({}, {"_id": 1, "name": 1}))
    if not devices:
        print(Fore.RED + "Erro: Rode o seed_data.py primeiro!")
        return

    print(Fore.YELLOW + "--- INICIANDO INGESTÃO DE DADOS EM TEMPO REAL ---")
    print(Fore.YELLOW + "Pressione Ctrl+C para parar...")

    total_inserted = 0
    
    while True:
        # Simula um lote de dados chegando (Batch Insert)
        batch = []
        # Escolhe 10 sensores aleatórios para "enviar dados" neste segundo
        active_sensors = random.sample(devices, 10) 

        for device in active_sensors:
            log = {
                "device_id": device["_id"],
                "timestamp": datetime.now(),
                "value": round(random.uniform(20.0, 100.0), 2), # Gera temperatura aleatória
                "type": "real-time-read"
            }
            batch.append(log)

        # Inserção rápida no MongoDB
        DB["sensor_logs"].insert_many(batch)
        total_inserted += len(batch)

        # Feedback visual de "Matrix"
        print(Fore.GREEN + f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Inseridos {len(batch)} logs... (Total: {total_inserted})")
        
        # Velocidade da simulação (0.5 segundos entre lotes)
        time.sleep(0.5)

if __name__ == "__main__":
    simulate_real_time_data()