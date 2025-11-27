# IoT Sensor Monitor - High Performance NoSQL Architecture

Este projeto foi desenvolvido como parte da disciplina de **Tópicos Avançados em Banco de Dados**. O objetivo é demonstrar padrões de arquitetura para sistemas de alto volume de escrita (Write-Heavy) e estratégias de correlação de dados via aplicação (Application-Side Joins) utilizando MongoDB.

## 🎯 Objetivo do Projeto
Simular um ambiente industrial de IoT onde sensores enviam dados continuamente. O sistema deve ser capaz de ingerir logs em alta velocidade e permitir consultas analíticas complexas sem utilizar JOINs no nível do banco de dados, garantindo escalabilidade horizontal.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.9+
* **Database:** MongoDB (NoSQL Document Store)
* **Drivers:** PyMongo
* **Data Generation:** Faker Library

## 🏗️ Arquitetura de Dados

Para otimizar a performance e evitar o limite de tamanho de documento do MongoDB (16MB), optamos pela estratégia de **Referencing** ao invés de **Embedding**.

### 1. Collection: `devices` (Metadados)
Armazena informações estáticas dos sensores. Leitura frequente, escrita rara.
```json
{
  "_id": ObjectId("..."),
  "sensor_id": "SENSOR-001",
  "location": "Setor A - Caldeira",
  "type": "Temperature",
  "status": "Active"
}