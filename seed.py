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

        dispositivos = []
        for i in range(1, num_dispositivos + 1):
            lat = round(random.uniform(-23.6000, -23.5000), 4)
            lon = round(random.uniform(-46.7000, -46.5000), 4)
            disp = Dispositivo(nome=f"Dispositivo {i}", latitude=lat, longitude=lon)
            dispositivos.append(disp)

        db.add_all(dispositivos)
        db.commit()

        for disp in dispositivos:
            db.refresh(disp)

        leituras = []
        id_sensor_base = 1

        for dispositivo in dispositivos:
            id_sensor_temp = id_sensor_base
            id_sensor_umid = id_sensor_base + 1
            id_sensor_base += 2

            tempo_atual = datetime.now() - timedelta(
                minutes=num_registros_por_dispositivo * 10
            )
            temp_atual = gerar_valor_natural("temperatura")
            umid_atual = gerar_valor_natural("umidade")

            for _ in range(num_registros_por_dispositivo):
                temp_atual = gerar_valor_natural("temperatura", temp_atual)
                umid_atual = gerar_valor_natural("umidade", umid_atual)

                leituras.append(
                    Leitura(
                        tipo="temperatura",
                        id_sensor=id_sensor_temp,
                        id_dispositivo=dispositivo.id,
                        valor=temp_atual,
                        criado_em=tempo_atual,
                    )
                )
                leituras.append(
                    Leitura(
                        tipo="umidade",
                        id_sensor=id_sensor_umid,
                        id_dispositivo=dispositivo.id,
                        valor=umid_atual,
                        criado_em=tempo_atual,
                    )
                )
                tempo_atual += timedelta(minutes=10)

        db.add_all(leituras)
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    qtd_disp = int(input("Informe a quantidade de dispositivos: "))
    qtd_reg = int(input("Informe a quantidade de registros por dispositivo: "))
    popular_banco(qtd_disp, qtd_reg)
