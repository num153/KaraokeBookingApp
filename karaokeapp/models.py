from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from karaokeapp import db, app


# 1. Bảng Vai trò người dùng (roles)
class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))

    # Relationship: Một role có nhiều users
    users = relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'


# 2. Bảng Người dùng (users)
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    # Relationships
    role = relationship('Role', back_populates='users')
    bills = relationship('Bill', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'


# 3. Bảng Trạng thái phòng (room_statuses)
class RoomStatus(db.Model):
    __tablename__ = 'room_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    # name có thể là: 'Available', 'Occupied', 'Booked'

    # Relationship: Một status có nhiều rooms
    rooms = relationship('Room', back_populates='status')

    def __repr__(self):
        return f'<RoomStatus {self.name}>'


# 4. Bảng Phòng hát (rooms)
class Room(db.Model):
    __tablename__ = 'rooms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)  # Sức chứa tối đa
    price_per_hour = Column(Numeric(10, 2), nullable=False)  # Giá thuê/giờ
    status_id = Column(Integer, ForeignKey('room_statuses.id'), nullable=False, default=1)

    # Relationships
    status = relationship('RoomStatus', back_populates='rooms')
    bills = relationship('Bill', back_populates='room')

    def __repr__(self):
        return f'<Room {self.name}>'


# 5. Bảng Khách hàng (customers)
class Customer(db.Model):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False, unique=True)
    monthly_visits = Column(Integer, default=0)  # Số lần đến trong tháng

    # Relationship: Một customer có nhiều bills
    bills = relationship('Bill', back_populates='customer')

    def __repr__(self):
        return f'<Customer {self.full_name}>'


# 6. Bảng Chính sách giảm giá (discount_policies)
class DiscountPolicy(db.Model):
    __tablename__ = 'discount_policies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    min_visit_req = Column(Integer, default=0)  # Số lần đến tối thiểu để được giảm giá
    discount_percent = Column(Numeric(5, 2), nullable=False)  # Phần trăm giảm giá
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationship: Một policy có nhiều bills áp dụng
    bills = relationship('Bill', back_populates='policy')

    def __repr__(self):
        return f'<DiscountPolicy {self.name}>'


# 7. Bảng Trạng thái hóa đơn (bill_statuses)
class BillStatus(db.Model):
    __tablename__ = 'bill_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    # name có thể là: 'Unpaid', 'Paid'

    # Relationship: Một status có nhiều bills
    bills = relationship('Bill', back_populates='status')

    def __repr__(self):
        return f'<BillStatus {self.name}>'


# 8. Bảng Hóa đơn (bills)
class Bill(db.Model):
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('discount_policies.id'))
    status_id = Column(Integer, ForeignKey('bill_statuses.id'), nullable=False, default=1)
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime)
    total_amount = Column(Numeric(15, 2), default=0.00)

    # Relationships
    customer = relationship('Customer', back_populates='bills')
    room = relationship('Room', back_populates='bills')
    user = relationship('User', back_populates='bills')
    policy = relationship('DiscountPolicy', back_populates='bills')
    status = relationship('BillStatus', back_populates='bills')
    bill_details = relationship('BillDetail', back_populates='bill', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Bill {self.id}>'


# 9. Bảng Dịch vụ (services)
class Service(db.Model):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)  # Đơn vị: Lon, Dĩa, Chai...
    price = Column(Numeric(10, 2), nullable=False)

    # Relationship: Một service có nhiều bill_details
    bill_details = relationship('BillDetail', back_populates='service')

    def __repr__(self):
        return f'<Service {self.name}>'


# 10. Bảng Chi tiết hóa đơn (bill_details)
class BillDetail(db.Model):
    __tablename__ = 'bill_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer, ForeignKey('bills.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_at_order = Column(Numeric(10, 2), nullable=False)  # Giá tại thời điểm đặt

    # Relationships
    bill = relationship('Bill', back_populates='bill_details')
    service = relationship('Service', back_populates='bill_details')

    def __repr__(self):
        return f'<BillDetail Bill:{self.bill_id} Service:{self.service_id}>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()