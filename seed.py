from app.db.database import SessionLocal
from app.models.dispositivo import Dispositivo
from app.models.leitura import Leitura


def popular_banco():
    db = SessionLocal()

    try:
        disp1 = Dispositivo(nome="Telhado Norte", latitude=-23.5505, longitude=-46.6333)
        disp2 = Dispositivo(nome="Telhado Sul", latitude=-23.5510, longitude=-46.6340)

        db.add_all([disp1, disp2])
        db.commit()
        db.refresh(disp1)
        db.refresh(disp2)

        leituras = [
            Leitura(
                tipo="temperatura", id_sensor=1, id_dispositivo=disp1.id, valor=25.5
            ),
            Leitura(tipo="umidade", id_sensor=2, id_dispositivo=disp1.id, valor=60.2),
            Leitura(
                tipo="temperatura", id_sensor=3, id_dispositivo=disp2.id, valor=26.1
            ),
            Leitura(tipo="umidade", id_sensor=4, id_dispositivo=disp2.id, valor=58.5),
        ]

        db.add_all(leituras)
        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    popular_banco()
