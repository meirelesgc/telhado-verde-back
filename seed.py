import random
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.models.dispositivo import Dispositivo
from app.models.leitura import Leitura


def limpar_banco(db):
    db.query(Leitura).delete()
    db.query(Dispositivo).delete()
    db.commit()


def gerar_valor_natural(tipo, valor_anterior=None):
    if tipo == "temperatura":
        if valor_anterior:
            return round(valor_anterior + random.uniform(-0.5, 0.5), 1)
        return round(random.uniform(15.0, 35.0), 1)
    elif tipo == "umidade":
        if valor_anterior:
            return round(valor_anterior + random.uniform(-2.0, 2.0), 1)
        return round(random.uniform(30.0, 90.0), 1)
    return 0.0


def popular_banco(num_dispositivos, num_registros_por_dispositivo):
    db = SessionLocal()

    try:
        limpar_banco(db)

        linhas = ["A", "B", "C", "D"]
        colunas = ["1", "2", "3", "4"]
        nomes_telhados = [f"Telhado Verde {l}{c}" for l in linhas for c in colunas]

        dispositivos = []
        for i in range(num_dispositivos):
            lat = round(random.uniform(-23.6000, -23.5000), 4)
            lon = round(random.uniform(-46.7000, -46.5000), 4)
            nome_escolhido = nomes_telhados[i % len(nomes_telhados)]

            disp = Dispositivo(nome=nome_escolhido, latitude=lat, longitude=lon)
            dispositivos.append(disp)

        db.add_all(dispositivos)
        db.commit()

        for disp in dispositivos:
            db.refresh(disp)

        leituras = []
        id_sensor_base = 1

        agora = datetime.now()
        sete_dias_atras = agora - timedelta(days=7)
        segundos_totais = int((agora - sete_dias_atras).total_seconds())

        for dispositivo in dispositivos:
            qtd_sensores = random.randint(1, 8)
            sensores = []

            for _ in range(qtd_sensores):
                tipo_sensor = random.choice(["temperatura", "umidade"])
                sensores.append({
                    "id_sensor": id_sensor_base,
                    "tipo": tipo_sensor,
                    "valor_atual": gerar_valor_natural(tipo_sensor),
                })
                id_sensor_base += 1

            timestamps = [
                sete_dias_atras + timedelta(seconds=random.randint(0, segundos_totais))
                for _ in range(num_registros_por_dispositivo)
            ]
            timestamps.sort()

            for tempo_atual in timestamps:
                for sensor in sensores:
                    sensor["valor_atual"] = gerar_valor_natural(
                        sensor["tipo"], sensor["valor_atual"]
                    )
                    leituras.append(
                        Leitura(
                            tipo=sensor["tipo"],
                            id_sensor=sensor["id_sensor"],
                            id_dispositivo=dispositivo.id,
                            valor=sensor["valor_atual"],
                            criado_em=tempo_atual,
                        )
                    )

        db.add_all(leituras)
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    qtd_disp = int(input("Informe a quantidade de telhados verdes: "))
    qtd_reg = int(input("Informe a quantidade de registros por telhado verde: "))
    popular_banco(qtd_disp, qtd_reg)
