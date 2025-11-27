import pymongo
import time
import os
from colorama import init, Fore, Style

init(autoreset=True)

CLIENT = pymongo.MongoClient("mongodb://localhost:27017/")
DB = CLIENT["iot_factory_db"]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_monitor():
    while True:
        # --- PASSO 1: Buscar Metadata (Quem são os sensores do Setor A?) ---
        target_sector = "Setor A"
        # Trazendo apenas o nome e ID para ser rápido
        devices_cursor = DB["devices"].find({"location": target_sector})
        target_devices = list(devices_cursor)
        target_ids = [d["_id"] for d in target_devices]

        if not target_ids:
            print("Nenhum sensor no Setor A. Rode o seed_data.py.")
            break

        # --- PASSO 2: Agregação em Tempo Real ---
        # Calcula média e pega a ÚLTIMA leitura inserida
        pipeline = [
            {"$match": {"device_id": {"$in": target_ids}}}, 
            {"$sort": {"timestamp": -1}}, # Ordena pelos mais recentes
            {"$group": {
                "_id": "$device_id", 
                "avg_temp": {"$avg": "$value"},
                "last_val": {"$first": "$value"}, # Pega o valor mais recente
                "count": {"$sum": 1}
            }}
        ]
        
        # Executa a query no MongoDB
        results = list(DB["sensor_logs"].aggregate(pipeline))
        results_map = {res["_id"]: res for res in results}

        # --- EXIBIÇÃO ---
        clear_screen()
        print(Fore.CYAN + "=====================================================")
        print(Fore.CYAN + f"   DASHBOARD TEMPO REAL - {target_sector.upper()}      ")
        print(Fore.CYAN + "=====================================================")
        
        # Calcular total de logs processados no setor agora
        total_processed = sum([r['count'] for r in results])
        print(Fore.YELLOW + f"📊 Logs Analisados Agora: {total_processed} (Crescendo...)")
        print("-" * 55)
        print(f"{'SENSOR':<15} | {'STATUS':<10} | {'MÉDIA':<10} | {'ÚLTIMA LEITURA'}")
        print("-" * 55)

        for device in target_devices:
            d_id = device["_id"]
            name = device["name"]
            
            if d_id in results_map:
                data = results_map[d_id]
                avg = data["avg_temp"]
                last = data["last_val"]
                count = data["count"]
                
                # Regra de negócio visual
                color = Fore.GREEN
                status = "NORMAL"
                if last > 80:
                    color = Fore.RED
                    status = "PERIGO"
                elif last > 60:
                    color = Fore.YELLOW
                    status = "ALERTA"

                print(color + f"{name:<15} | {status:<10} | {avg:.1f}°C     | {last:.1f}°C (n={count})")
            else:
                print(Fore.WHITE + f"{name:<15} | AGUARDANDO DADOS...")

        print(Style.RESET_ALL + "\n-----------------------------------------------------")
        print("Pressione Ctrl+C para encerrar o monitor.")
        
        time.sleep(2) # Atualiza a tela a cada 2 segundos

if __name__ == "__main__":
    run_monitor()