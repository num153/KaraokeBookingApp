"""
Data Access Object (DAO) - Quản lý tất cả truy vấn database
"""
from datetime import datetime, date
from sqlalchemy import func
from karaokeapp import db
from karaokeapp.models import (
    Room, Bill, Customer, RoomStatus,
    BillStatus, Service, BillDetail, DiscountPolicy
)


# ==================== ROOM DAO ====================

def get_all_rooms():
    """Lấy tất cả phòng"""
    return Room.query.order_by(Room.id).all()


def search_rooms(keyword):
    """Tìm kiếm phòng theo tên"""
    return Room.query.filter(Room.name.contains(keyword)).order_by(Room.id).all()


def get_available_rooms():
    """Lấy danh sách phòng còn trống"""
    return Room.query.join(RoomStatus) \
        .filter(RoomStatus.name == 'Available') \
        .order_by(Room.name) \
        .all()


def get_room_by_id(room_id):
    """Lấy thông tin phòng theo ID"""
    return Room.query.get(room_id)


def update_room_status(room_id, status_id):
    """Cập nhật trạng thái phòng"""
    room = Room.query.get(room_id)
    if room:
        room.status_id = status_id
        db.session.commit()
        return True
    return False


# ==================== STATS DAO ====================

def get_room_stats():
    """Lấy thống kê phòng"""
    total_rooms = Room.query.count()
    available_rooms = Room.query.join(RoomStatus) \
        .filter(RoomStatus.name == 'Available').count()
    occupied_rooms = Room.query.join(RoomStatus) \
        .filter(RoomStatus.name == 'Occupied').count()

    return {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms
    }


def get_today_revenue():
    """Lấy doanh thu hôm nay"""
    today = date.today()
    revenue = db.session.query(func.sum(Bill.total_amount)) \
        .filter(Bill.status_id == 2) \
        .filter(func.date(Bill.end_time) == today) \
        .scalar()
    return revenue or 0


# ==================== CUSTOMER DAO ====================

def find_customer_by_phone(phone):
    """Tìm khách hàng theo SĐT"""
    return Customer.query.filter_by(phone=phone).first()


def create_customer(full_name, phone):
    """Tạo khách hàng mới"""
    customer = Customer(
        full_name=full_name,
        phone=phone,
        monthly_visits=0
    )
    db.session.add(customer)
    db.session.commit()
    return customer


def update_customer_name(customer, new_name):
    """Cập nhật tên khách hàng"""
    customer.full_name = new_name
    db.session.commit()


def increase_customer_visits(customer_id):
    """Tăng số lần đến của khách hàng"""
    customer = Customer.query.get(customer_id)
    if customer:
        customer.monthly_visits += 1
        db.session.commit()


# ==================== BILL DAO ====================

def create_bill(customer_id, room_id, user_id, start_time, status_id=1):
    """Tạo hóa đơn mới"""
    bill = Bill(
        customer_id=customer_id,
        room_id=room_id,
        user_id=user_id,
        policy_id=None,
        status_id=status_id,
        start_time=start_time,
        end_time=None,
        total_amount=0
    )
    db.session.add(bill)
    db.session.commit()
    return bill


def get_recent_bookings(limit=5):
    """Lấy danh sách booking gần đây"""
    return Bill.query \
        .filter(Bill.status_id == 1) \
        .order_by(Bill.start_time.desc()) \
        .limit(limit) \
        .all()


def get_bill_by_id(bill_id):
    """Lấy hóa đơn theo ID"""
    return Bill.query.get(bill_id)


def get_active_bill_by_room(room_id):
    """Lấy hóa đơn đang active của phòng"""
    return Bill.query \
        .filter_by(room_id=room_id, status_id=1) \
        .order_by(Bill.start_time.desc()) \
        .first()


def update_bill_end_time(bill_id, end_time):
    """Cập nhật thời gian kết thúc"""
    bill = Bill.query.get(bill_id)
    if bill:
        bill.end_time = end_time
        db.session.commit()
        return True
    return False

# ==================== BILL CALCULATION ====================
def calculate_bill_info(bill_id):
    """Tính toán đầy đủ thông tin bill (dùng chung cho nhiều chỗ)"""
    from decimal import Decimal

    bill = Bill.query.get(bill_id)
    if not bill:
        return None

    now = datetime.now()

    # Tính thời gian đã sử dụng
    time_used_seconds = (now - bill.start_time).total_seconds()
    time_used = Decimal(str(time_used_seconds / 3600))  # giờ

    # Tính tiền phòng
    room_price = Decimal(str(bill.room.price_per_hour)) * time_used

    # Tính tiền dịch vụ
    service_total = db.session.query(func.sum(BillDetail.quantity * BillDetail.price_at_order)) \
                        .filter(BillDetail.bill_id == bill_id) \
                        .scalar() or Decimal('0')

    # Tổng trước giảm giá
    subtotal = room_price + Decimal(str(service_total))

    # Kiểm tra giảm giá
    discount = Decimal('0')
    discount_policy = None
    if bill.customer and bill.customer.monthly_visits >= 10:
        discount_policy = check_customer_discount_eligibility(bill.customer.id)
        if discount_policy:
            discount_percent = Decimal(str(discount_policy.discount_percent)) / Decimal('100')
            discount = subtotal * discount_percent

    # Tổng tiền
    total = subtotal - discount

    # Kiểm tra hết giờ (mặc định 2 giờ)
    expected_duration = Decimal('2.0')
    is_overtime = time_used > expected_duration

    return {
        'bill': bill,
        'time_used': float(time_used),
        'time_used_decimal': time_used,
        'is_overtime': is_overtime,
        'room_price': room_price,
        'service_total': service_total,
        'subtotal': subtotal,
        'discount': discount,
        'discount_policy': discount_policy,
        'total': total
    }


def calculate_bill_total(bill_id):
    """Tính tổng tiền hóa đơn (dùng khi thanh toán)"""
    from decimal import Decimal

    bill = Bill.query.get(bill_id)
    if not bill:
        return 0

    # Tính tiền phòng
    if bill.end_time:
        hours_seconds = (bill.end_time - bill.start_time).total_seconds()
        hours = Decimal(str(hours_seconds / 3600))
        room_price = Decimal(str(bill.room.price_per_hour)) * hours
    else:
        room_price = Decimal('0')

    # Tính tiền dịch vụ
    service_price_query = db.session.query(func.sum(BillDetail.quantity * BillDetail.price_at_order)) \
        .filter(BillDetail.bill_id == bill_id) \
        .scalar()

    service_price = Decimal(str(service_price_query)) if service_price_query else Decimal('0')

    # Tổng trước giảm giá
    subtotal = room_price + service_price

    # Áp dụng giảm giá nếu có
    discount = Decimal('0')
    if bill.policy_id:
        policy = DiscountPolicy.query.get(bill.policy_id)
        if policy and policy.is_active:
            discount_percent = Decimal(str(policy.discount_percent)) / Decimal('100')
            discount = subtotal * discount_percent

    total = subtotal - discount

    # Cập nhật vào database
    bill.total_amount = float(total)
    db.session.commit()

    return float(total)


# ==================== SERVICE DAO ====================

def get_all_services():
    """Lấy tất cả dịch vụ"""
    return Service.query.order_by(Service.name).all()


def search_services(keyword):
    """Tìm kiếm dịch vụ"""
    return Service.query.filter(Service.name.contains(keyword)).all()


def get_service_by_id(service_id):
    """Lấy dịch vụ theo ID"""
    return Service.query.get(service_id)


# ==================== BILL DETAIL DAO ====================

def add_service_to_bill(bill_id, service_id, quantity):
    """Thêm dịch vụ vào hóa đơn"""
    service = Service.query.get(service_id)
    if not service:
        return False

    # Kiểm tra dịch vụ đã tồn tại trong bill chưa
    existing_detail = BillDetail.query \
        .filter_by(bill_id=bill_id, service_id=service_id) \
        .first()

    if existing_detail:
        # Cập nhật số lượng
        existing_detail.quantity += quantity
    else:
        # Tạo mới
        detail = BillDetail(
            bill_id=bill_id,
            service_id=service_id,
            quantity=quantity,
            price_at_order=service.price
        )
        db.session.add(detail)

    db.session.commit()
    return True


def get_bill_details(bill_id):
    """Lấy chi tiết dịch vụ của hóa đơn"""
    return BillDetail.query.filter_by(bill_id=bill_id).all()


def remove_service_from_bill(detail_id):
    """Xóa dịch vụ khỏi hóa đơn"""
    detail = BillDetail.query.get(detail_id)
    if detail:
        db.session.delete(detail)
        db.session.commit()
        return True
    return False


# ==================== DISCOUNT POLICY DAO ====================

def get_active_policies():
    """Lấy các chính sách đang active"""
    now = datetime.now()
    return DiscountPolicy.query \
        .filter(DiscountPolicy.is_active == True) \
        .filter(DiscountPolicy.start_date <= now) \
        .filter(DiscountPolicy.end_date >= now) \
        .all()


def check_customer_discount_eligibility(customer_id):
    """Kiểm tra khách hàng có đủ điều kiện giảm giá không"""
    customer = Customer.query.get(customer_id)
    if not customer:
        return None

    # Lấy policy phù hợp
    policies = get_active_policies()
    for policy in policies:
        if customer.monthly_visits >= policy.min_visit_req:
            return policy

    return None