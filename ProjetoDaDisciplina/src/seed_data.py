from pymongo import MongoClient
from faker import Faker
import random
from colorama import init, Fore

init(autoreset=True)

def main():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['iot_factory_db']
    
    # Limpar tudo para começar do zero
    print(Fore.CYAN + "Resetando a fábrica...")
    db['devices'].delete_many({})
    db['sensor_logs'].delete_many({})

    locations = ['Setor A', 'Setor B', 'Setor C']
    types = ['Temperature', 'Pressure', 'Vibration']
    
    devices = []
    print(Fore.CYAN + "Instalando 50 novos sensores...")
    
    # CRIANDO 50 SENSORES (Para o monitor ficar cheio)
    for i in range(1, 51):
        device = {
            'name': f"Sensor-{i:02d}",
            'location': random.choice(locations), # Distribui aleatoriamente
            'type': random.choice(types),
            'status': 'active'
        }
        devices.append(device)

    db['devices'].insert_many(devices)
    print(Fore.GREEN + f"Sucesso! {len(devices)} sensores configurados e prontos para receber dados.")

if __name__ == '__main__':
    main()