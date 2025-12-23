from flask import render_template, request
from sqlalchemy import func
from datetime import datetime, date

from karaokeapp import app, db
from karaokeapp.models import Room, Bill, Customer, RoomStatus


@app.route('/')
def home():
    # Lấy keyword tìm kiếm từ query string
    keyword = request.args.get('keyword', '').strip()

    # Query phòng với filter search
    if keyword:
        rooms = Room.query.filter(Room.name.contains(keyword)).all()
    else:
        rooms = Room.query.order_by(Room.id).all()

    # Thống kê số lượng phòng
    total_rooms = Room.query.count()
    available_rooms = Room.query.join(RoomStatus).filter(RoomStatus.name == 'Available').count()
    occupied_rooms = Room.query.join(RoomStatus).filter(RoomStatus.name == 'Occupied').count()

    # Tính doanh thu hôm nay (chỉ bill đã thanh toán)
    today = date.today()
    today_revenue = db.session.query(func.sum(Bill.total_amount)) \
                        .filter(Bill.status_id == 2) \
                        .filter(func.date(Bill.end_time) == today) \
                        .scalar() or 0

    # Lấy danh sách booking gần đây (5 booking mới nhất)
    recent_bookings = Bill.query \
        .filter(Bill.status_id == 1) \
        .order_by(Bill.start_time.desc()) \
        .limit(5) \
        .all()

    # Đóng gói stats
    stats = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'today_revenue': today_revenue
    }

    return render_template('index.html',
                           rooms=rooms,
                           stats=stats,
                           recent_bookings=recent_bookings)
# ==================== ĐẶT PHÒNG ====================
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    # Logic đặt phòng
    pass


# ==================== QUẢN LÝ DỊCH VỤ ====================
@app.route('/services')
def services():
    # Logic quản lý dịch vụ
    pass


# ==================== THANH TOÁN ====================
@app.route('/payment/<int:bill_id>', methods=['GET', 'POST'])
def payment(bill_id):
    # Logic thanh toán
    pass


# ==================== BÁO CÁO ====================
@app.route('/reports')
def reports():
    # Logic báo cáo
    pass
