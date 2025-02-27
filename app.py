from decimal import Decimal
from flask import Flask, jsonify, make_response, render_template, request
from sqlalchemy import create_engine, and_, func, or_
from sqlalchemy.orm import sessionmaker
from models import (
    Model, 
    Customer, 
    ReverseOrders, 
    ReverseOrderStatuses,
    ReverseOrderImages, 
    VariantStorage, 
    Variants, 
    Storages, 
    VariantStorageBuyBack,
    ModelStorage,
    QeGeneralOperation,
    QeIntactDisplay,
    QeDisplayCondition,
    QeDeviceCondition,
    QeGlassCracks,
    QeDamagedDevice,
    QeWaterContact,
    QeWorkingUnlockid,
    QeBatteryLevel,
)

def create_engine_url(db_config):
    return f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"

db_config = {
    "host": "localhost",
    "database": "prova",
    "user": "postgres", 
    "password": "prova"
}

engine = create_engine(create_engine_url(db_config), echo=True)
Session = sessionmaker(bind=engine)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/api/get-image/<int:order_id>")
def get_image(order_id):
    session = Session()
    print(f"order_id: {order_id}")

    try:
        image = session.query(ReverseOrderImages).filter_by(reverse_order_id=order_id).first()
        if not image:
            return jsonify({"error": "Image not found"}), 404
        
        response = make_response(image.image_data)
        response.headers.set('Content-Type', 'image/jpeg')
        return response

    except Exception as e:
        print(f"Error fetching image: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
        
@app.route("/api/reverse-orders")
def get_reverse_orders_for_table():
    try:
        session = Session()
        orders = (
            session.query(
                ReverseOrders.id,
                ReverseOrders.price,
                ReverseOrders.datetime,
                ReverseOrderStatuses.name.label("status_name"),
                ReverseOrders.customer_id,
                Customer.name.label("customer_name"),
                Customer.last_name.label("customer_last_name"),
                ReverseOrders.variant_storage_id,
                VariantStorageBuyBack.base_price,
                Storages.storage,
                Variants.color_name,
                Model.model_name,
                QeGeneralOperation.percentage.label("general_operation_percentage"),
                QeIntactDisplay.percentage.label("intact_display_percentage"),
                QeDisplayCondition.percentage.label("display_condition_percentage"),
                QeDeviceCondition.percentage.label("device_condition_percentage"),
                QeGlassCracks.percentage.label("glass_cracks_percentage"),
                QeDamagedDevice.percentage.label("damaged_device_percentage"),
                QeWaterContact.percentage.label("water_contact_percentage"),
                QeWorkingUnlockid.percentage.label("working_unlockid_percentage"),
                QeBatteryLevel.money.label("battery_level_money"),
                ReverseOrderImages.id.label("image_id")
            )
            .join(ReverseOrderStatuses, ReverseOrders.status_id == ReverseOrderStatuses.id)
            .join(Customer, ReverseOrders.customer_id == Customer.id)
            .join(VariantStorageBuyBack, ReverseOrders.variant_storage_id == VariantStorageBuyBack.id)
            .join(Variants, Variants.id == VariantStorageBuyBack.variant_id)
            .join(Model, Model.id == Variants.model_id)
            .join(Storages, Storages.id == VariantStorageBuyBack.storage_id)
            .join(QeGeneralOperation, QeGeneralOperation.id == ReverseOrders.qe_1)
            .join(QeIntactDisplay, QeIntactDisplay.id == ReverseOrders.qe_2)
            .join(QeDisplayCondition, QeDisplayCondition.id == ReverseOrders.qe_3)
            .join(QeDeviceCondition, QeDeviceCondition.id == ReverseOrders.qe_4)
            .join(QeGlassCracks, QeGlassCracks.id == ReverseOrders.qe_5)
            .join(QeDamagedDevice, QeDamagedDevice.id == ReverseOrders.qe_6)
            .join(QeWaterContact, QeWaterContact.id == ReverseOrders.qe_7)
            .join(QeWorkingUnlockid, QeWorkingUnlockid.id == ReverseOrders.qe_8)
            .join(QeBatteryLevel, QeBatteryLevel.id == ReverseOrders.qe_9)
            .join(ReverseOrderImages, ReverseOrderImages.reverse_order_id == ReverseOrders.id)
            .all()
        )

        results = [
            {
                "order_id": order.id,
                "price": float(order.price),
                "datetime": order.datetime.isoformat(),
                "status_name": order.status_name,
                "customer_name": f"{order.customer_name} {order.customer_last_name}",
                "variant_storage_id": order.variant_storage_id,
                "base_price": float(order.base_price),
                "storage": order.storage,
                "color_name": order.color_name,
                "model_name": order.model_name,
                "general_operation_percentage": float(order.general_operation_percentage),
                "intact_display_percentage": float(order.intact_display_percentage),
                "display_condition_percentage": float(order.display_condition_percentage),
                "device_condition_percentage": float(order.device_condition_percentage),
                "glass_cracks_percentage": float(order.glass_cracks_percentage),
                "damaged_device_percentage": float(order.damaged_device_percentage),
                "water_contact_percentage": float(order.water_contact_percentage),
                "working_unlockid_percentage": float(order.working_unlockid_percentage),
                "battery_level_money": float(order.battery_level_money),
                "image_url": f"/api/get-image/{order.image_id}" if order.image_id else None  # URL per l'immagine
            }
            for order in orders
        ]
        print(results)
        
        return jsonify(calculate_price(results))
    except Exception as e:
        print(f"Error fetching reverse orders: {e}")
        return []


def calculate_price(orders):
    for order in orders:
        calculated_price = (
            order["base_price"]
            + (order["base_price"] * order["general_operation_percentage"] / 100)
            + (order["base_price"] * order["intact_display_percentage"] / 100)
            + (order["base_price"] * order["display_condition_percentage"] / 100)
            + (order["base_price"] * order["device_condition_percentage"] / 100)
            + (order["base_price"] * order["glass_cracks_percentage"] / 100)
            + (order["base_price"] * order["damaged_device_percentage"] / 100)
            + (order["base_price"] * order["water_contact_percentage"] / 100)
            + (order["base_price"] * order["working_unlockid_percentage"] / 100)
            - order["battery_level_money"]
        )
        order["price"] = 0 if calculated_price < 0 else calculated_price
    return orders
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5026)
