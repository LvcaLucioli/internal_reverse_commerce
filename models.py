from sqlalchemy import Column, Integer, String, Float, BigInteger, Date, UniqueConstraint, Numeric, Text, ForeignKey, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import DateTime, PrimaryKeyConstraint
from datetime import datetime
from sqlalchemy.event import listens_for

Base = declarative_base()

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    imei_id = Column(BigInteger, ForeignKey('imei_files.id'))
    selling_price = Column(Numeric, nullable=False)
    margin = Column(Numeric)
    sku = Column(String(255))
    model = Column(String(255))
    order_number = Column(String(255))
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    test_sale_delta = Column(Numeric(10, 2), nullable=True)
    proforma_sale_delta = Column(Numeric(10, 2), nullable=True)
    accessory_cost = Column(Numeric, nullable=True)
    serie = Column(String(255), ForeignKey('models.sku_root', ondelete='SET NULL'))

    variant_storage_id = Column(Integer, ForeignKey('variant_storage.id'), nullable=True)

    variant_storage = relationship('VariantStorage', back_populates='sales')

    imei = relationship('ImeiFile', back_populates='sales')

    def __repr__(self):
        return f"<Sale(id={self.id}, selling_price={self.selling_price}, sku={self.sku}, model={self.model})>"

    __table_args__ = (
        UniqueConstraint('imei_id', 'order_number', 'store_id', name='imei_order_number_store_unique'), 
    )
    
class ImeiFile(Base):
    __tablename__ = 'imei_files'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    imei = Column(String(20), nullable=False, unique=True)
    cost = Column(Numeric)
    sku = Column(String(255))
    grade = Column(String(50))
    supplier_id = Column(BigInteger, ForeignKey('suppliers.id'))
    proforma_id = Column(BigInteger, ForeignKey('proforma.id'))
    serial = Column(String(255))
    model_name = Column(Text)
    memory = Column(String(10))

    supplier = relationship('Supplier', back_populates='imei_files')
    proforma = relationship('Proforma', back_populates='imei_files')
    sales = relationship('Sale', back_populates='imei', cascade='all, delete-orphan')
    tests = relationship('Test', back_populates='imei_file')

    def __repr__(self):
        return f"<ImeiFile(id={self.id}, imei={self.imei}, model_name={self.model_name})>"

    __table_args__ = (
        UniqueConstraint('imei', name='imei_files_imei_key'),
    )
    
@listens_for(Sale, 'before_insert')
@listens_for(Sale, "before_update")
def before_sale_insert(mapper, connection, sale):
    if sale.sku:
        variant_storage = connection.execute(
            VariantStorage.__table__.select().where(VariantStorage.sku == sale.sku)
        ).fetchone()

        if variant_storage:
            sale.variant_storage_id = variant_storage.id
    
class Order(Base):
    __tablename__ = 'orders'
    
    order_number = Column(String(255), nullable=False, primary_key=True)
    store_id = Column(Integer, nullable=False, primary_key=True)
    customer_id = Column(BigInteger, nullable=False)
    date = Column(Date, nullable=False)
    country = Column(String(255))
    unapp_notes = Column(Text)
    refund = Column(Numeric)
    total = Column(Numeric)
    notes = Column(Text)

    __table_args__ = (
        UniqueConstraint('order_number', 'store_id', name='unique_order_number_store_id'),
    )
    
    def __repr__(self):
        return f"<Order(order_number={self.order_number}, store_id={self.store_id}, date={self.date})>"
    
class Proforma(Base):
    __tablename__ = 'proforma'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    supplier_id = Column(BigInteger, ForeignKey('suppliers.id'), nullable=False)
    date = Column(Date)
    created_at = Column(DateTime, default=datetime.now())

    
    supplier = relationship('Supplier', back_populates='proformas')
    imei_files = relationship('ImeiFile', back_populates='proforma')
    
    def __repr__(self):
        return f"<Proforma(id={self.id}, name={self.name}, date={self.date}, created_at={self.created_at})>"

    __table_args__ = (
        UniqueConstraint('name', name='proforma_name_key'),
    )

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    
    imei_files = relationship('ImeiFile', back_populates='supplier')
    proformas = relationship('Proforma', back_populates='supplier')
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name})>"

    __table_args__ = (
    )
    

class Store(Base):
    __tablename__ = 'stores'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), unique=True)
    alias = Column(String(255))

    def __repr__(self):
        return f"<Store(id={self.id}, name='{self.name}', alias='{self.alias}')>"

    __table_args__ = (
        UniqueConstraint('name', name='stores_name_key'),
    )
    
class Test(Base):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    imei_id = Column(BigInteger, ForeignKey('imei_files.id', ondelete='CASCADE'), nullable=False)
    notes = Column(Text)
    date = Column(DateTime, nullable=False)
    operator_code = Column(String(50), ForeignKey('operators.code'), nullable=False)
    result = Column(String)
    capacity_deviation = Column(Numeric(10, 2))
    has_too_many_cycles = Column(Boolean)
    has_missing_information = Column(Boolean)
    battery_level = Column(Integer)
    is_not_nb = Column(Boolean)
    should_be_nb = Column(Boolean)
    has_zero_capacity = Column(Boolean)
    battery_health = Column(Integer)
    cycle_count = Column(Integer)
    region_code = Column(String(255))
    grade = Column(String(50))
    proforma_test_delta = Column(Numeric(10, 2))

    imei_file = relationship("ImeiFile", back_populates="tests")
    operator = relationship('Operator', back_populates='tests')  # Questa relazione

    def __repr__(self):
        return f"<Test(id={self.id}, imei_id={self.imei_id}, date={self.date}, battery_health={self.battery_health})>"

class Operator(Base):
    __tablename__ = 'operators'

    code = Column(String(50), primary_key=True, nullable=False)
    name = Column(String(100))
    target = Column(Integer, default=0)
    room = Column(Integer)

    tests = relationship('Test', back_populates='operator', primaryjoin="Operator.code==Test.operator_code")

    def __repr__(self):
        return f"<Operator(code={self.code}, name={self.name}, target={self.target}, room={self.room})>"

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    province = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    zip_code = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    shipping_name = Column(String(255), nullable=False)
    company = Column(String(255))

    __table_args__ = (
        UniqueConstraint('name', 'last_name', 'user_id', 'email', 
                         'phone_number', 'city', 'province', 
                         'country', 'zip_code', 'address', 
                         'shipping_name', 'company', 
                         name='unique_customer_info'),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, last_name={self.last_name}, email={self.email})>"
    
class CustomerDefect(Base):
    __tablename__ = 'customer_defects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(50), nullable=False)
    imei_id = Column(Integer, ForeignKey('imei_files.id'), nullable=False)
    insertion_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)
    detection_date = Column(Date, nullable=False)
    details_id = Column(Integer, ForeignKey('defect_details.id'), nullable=True)
    swap = Column(Text, nullable=True)
    new_battery_test = Column(Boolean, nullable=True)

    imei = relationship('ImeiFile', backref='customer_defects')
    store = relationship('Store', backref='customer_defects')
    details = relationship('DefectDetail', back_populates='customer_defect', overlaps='customer_defects_details,details')
    topics = relationship('CustomerDefectTopic', back_populates='defect')
class DefectDetail(Base):
    __tablename__ = 'defect_details'

    id = Column(Integer, primary_key=True, autoincrement=True) 
    description = Column(String(255), nullable=False, unique=True) 

    customer_defect = relationship('CustomerDefect', back_populates='details', overlaps='customer_defects_details,details')  

class MarginsSettings(Base):
    __tablename__ = 'margins_settings'

    battery_cost = Column(Numeric(10, 2), nullable=False)
    percentage_fee = Column(Numeric(5, 2), nullable=False)
    return_shipping = Column(Numeric(10, 2), nullable=False)
    shipping_fee = Column(Numeric(10, 2), nullable=False)
    box_cost = Column(Numeric(10, 2), nullable=False)
    cable_cost = Column(Numeric(10, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('start_date', 'end_date'),
    )

    def __repr__(self):
        return (f"<MarginsSettings(battery_cost={self.battery_cost}, "
                f"percentage_fee={self.percentage_fee}, return_shipping={self.return_shipping}, "
                f"shipping_fee={self.shipping_fee}, box_cost={self.box_cost}, "
                f"cable_cost={self.cable_cost}, start_date={self.start_date}, end_date={self.end_date})>")
    
class CustomerDefectTopic(Base):
    __tablename__ = 'customer_defect_topics'

    # id = Column(Integer, primary_key=True)
    customer_defect_id = Column(Integer, ForeignKey('customer_defects.id'), primary_key=True, nullable=False)
    defect_topic_id = Column(Integer, ForeignKey('defects_topics.id'), primary_key=True, nullable=False)

    defect = relationship("CustomerDefect", back_populates="topics")
    topic = relationship("DefectTopic", back_populates="defects")
    
class DefectTopic(Base):
    __tablename__ = 'defects_topics'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    defects = relationship("CustomerDefectTopic", back_populates="topic")

    def __repr__(self):
        return f"<DefectTopic(id={self.id}, name='{self.name}')>"

class Model(Base):
    __tablename__ = 'models'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(255), nullable=False, unique=True)
    sku_root = Column(String(255), nullable=False, unique=True)
    reverse_commerce = Column(Integer, default=0) 
    
    # Relazione con Sales
    # sales = relationship(
    #     "Sale",
    #     back_populates="model",
    #     primaryjoin="Model.sku_root == Sale.serie"
    # )


class Storages(Base):
    __tablename__ = 'storages'

    id = Column(Integer, primary_key=True)
    storage = Column(String(255), nullable=False)
    sku_storage = Column(String(255), nullable=False)


class ModelStorage(Base):
    __tablename__ = 'model_storage'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('models.id', ondelete='CASCADE'), nullable=False)
    storage_id = Column(Integer, ForeignKey('storages.id', ondelete='CASCADE'), nullable=False)


class Variants(Base):
    __tablename__ = 'variants'

    id = Column(Integer, primary_key=True)
    color_name = Column(String(255), nullable=False)
    alias = Column(String(255), nullable=False)
    color_hex = Column(String(7), nullable=False)
    sku_color = Column(String(255), nullable=False)
    model_id = Column(Integer, ForeignKey('models.id'), nullable=False)

class Grades(Base):
    __tablename__ = 'grades'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    sku_grade = Column(String(255), nullable=False)
    
class VariantStorageBuyBack(Base):
    __tablename__ = 'variant_storage_buy_back'

    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey('variants.id'), nullable=False)
    storage_id = Column(Integer, ForeignKey('storages.id'), nullable=False)
    base_price = Column(Numeric(10, 2))

class VariantStorage(Base):
    __tablename__ = 'variant_storage'

    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey('variants.id'), nullable=False)
    storage_id = Column(Integer, ForeignKey('storages.id'), nullable=False)
    backmarket_price = Column(Numeric(10, 2))
    refurbed_price = Column(Numeric(10, 2))
    new_battery = Column(Integer, default=0)
    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=False)
    sku = Column(String(255))

    sales = relationship('Sale', back_populates='variant_storage')

    
@listens_for(VariantStorage, "before_insert")
@listens_for(VariantStorage, "before_update")
def generate_sku(mapper, connection, target):
    """Genera automaticamente lo SKU per la tabella variant_storage prima di inserire o aggiornare un record."""
    
    session = Session.object_session(target)

    # Recupera i dati collegati dalle altre tabelle
    variant = session.query(Variants).filter(Variants.id == target.variant_id).first()
    storage = session.query(Storages).filter(Storages.id == target.storage_id).first()
    grade = session.query(Grades).filter(Grades.id == target.grade_id).first()
    model = session.query(Model).filter(Model.id == variant.model_id).first()

    # Verifica che tutti i dati siano presenti
    if variant and storage and grade and model:
        # Costruisce lo SKU concatenando i vari pezzi
        sku = f"{model.sku_root}{storage.sku_storage}{variant.sku_color}{grade.sku_grade}"

        # Se new_battery è 1, aggiunge "-NB" alla fine dello SKU
        if target.new_battery:
            sku += "-NB"

        target.sku = sku
class ReverseOrders(Base):
    __tablename__ = 'reverse_orders'

    id = Column(Integer, primary_key=True)
    price = Column(Numeric(10, 2), nullable=False)
    datetime = Column(DateTime, default=datetime.now())
    variant_storage_id = Column(Integer, ForeignKey('variant_storage.id'), nullable=False)
    status_id = Column(Integer, ForeignKey('reverse_order_statuses.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    message = Column(Text)

    qe_1 = Column(Integer, ForeignKey('qe_general_operation.id', ondelete="SET NULL"))
    qe_2 = Column(Integer, ForeignKey('qe_intact_display.id', ondelete="SET NULL"))
    qe_3 = Column(Integer, ForeignKey('qe_display_condition.id', ondelete="SET NULL"))
    qe_4 = Column(Integer, ForeignKey('qe_device_condition.id', ondelete="SET NULL"))
    qe_5 = Column(Integer, ForeignKey('qe_glass_cracks.id', ondelete="SET NULL"))
    qe_6 = Column(Integer, ForeignKey('qe_damaged_device.id', ondelete="SET NULL"))
    qe_7 = Column(Integer, ForeignKey('qe_water_contact.id', ondelete="SET NULL"))
    qe_8 = Column(Integer, ForeignKey('qe_working_unlockid.id', ondelete="SET NULL"))
    qe_9 = Column(Integer, ForeignKey('qe_battery_level.id', ondelete="SET NULL"))


class ReverseOrderStatuses(Base):
    __tablename__ = 'reverse_order_statuses'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class ReverseOrderImages(Base):
    __tablename__ = 'reverse_order_images'

    id = Column(Integer, primary_key=True)
    reverse_order_id = Column(Integer, ForeignKey('reverse_orders.id'), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    image_name = Column(String(255), nullable=False)


class QualityEvaluation(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeGeneralOperation(QualityEvaluation):
    __tablename__ = 'qe_general_operation'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeIntactDisplay(QualityEvaluation):
    __tablename__ = 'qe_intact_display'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeDisplayCondition(QualityEvaluation):
    __tablename__ = 'qe_display_condition'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeDeviceCondition(QualityEvaluation):
    __tablename__ = 'qe_device_condition'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeGlassCracks(QualityEvaluation):
    __tablename__ = 'qe_glass_cracks'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeDamagedDevice(QualityEvaluation):
    __tablename__ = 'qe_damaged_device'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeWaterContact(QualityEvaluation):
    __tablename__ = 'qe_water_contact'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)

class QeWorkingUnlockid(QualityEvaluation):
    __tablename__ = 'qe_working_unlockid'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)


class QeBatteryLevel(Base):
    __tablename__ = 'qe_battery_level'
    id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)
    money = Column(Numeric(5, 2), nullable=False)
    
