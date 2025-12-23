from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import func
from datetime import datetime, date

from karaokeapp import app, db
from karaokeapp import dao
from karaokeapp.models import Room, Bill, Customer, RoomStatus


# ==================== TRANG CHỦ ====================
@app.route('/')
def home():
    # Lấy keyword tìm kiếm
    keyword = request.args.get('keyword', '').strip()

    # Lấy danh sách phòng
    rooms = dao.search_rooms(keyword) if keyword else dao.get_all_rooms()

    # Lấy thống kê
    stats = dao.get_room_stats()
    stats['today_revenue'] = dao.get_today_revenue()

    # Lấy booking gần đây
    recent_bookings = dao.get_recent_bookings(limit=5)

    return render_template('index.html',
                           rooms=rooms,
                           stats=stats,
                           recent_bookings=recent_bookings)
# # ==================== ĐẶT PHÒNG ====================
# @app.route('/booking', methods=['GET', 'POST'])
# def booking():
#     if request.method == 'POST':
#         # Xử lý form đặt phòng
#         customer_name = request.form.get('customer_name')
#         customer_phone = request.form.get('customer_phone')
#         room_id = request.form.get('room_id')
#         num_people = request.form.get('num_people')
#         start_time = request.form.get('start_time')
#         notes = request.form.get('notes')
#
#         # TODO: Xử lý logic đặt phòng (sẽ code sau)
#         # - Kiểm tra số người <= capacity
#         # - Kiểm tra phòng còn trống
#         # - Tạo Bill mới
#         # - Cập nhật trạng thái phòng
#
#         return redirect(url_for('home'))
#
#     # GET request - Hiển thị form
#     available_rooms = Room.query.join(RoomStatus) \
#         .filter(RoomStatus.name == 'Available') \
#         .order_by(Room.name) \
#         .all()
#
#     return render_template('booking.html', rooms=available_rooms)
# ==================== ĐẶT PHÒNG ====================
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        try:
            # Lấy dữ liệu form
            customer_name = request.form.get('customer_name').strip()
            customer_phone = request.form.get('customer_phone').strip()
            room_id = int(request.form.get('room_id'))
            num_people = int(request.form.get('num_people'))
            start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')

            # Validate thời gian
            if start_time < datetime.now():
                flash('Thời gian bắt đầu phải lớn hơn hiện tại!', 'danger')
                return redirect(url_for('booking'))

            # Kiểm tra phòng
            room = dao.get_room_by_id(room_id)
            if not room:
                flash('Phòng không tồn tại!', 'danger')
                return redirect(url_for('booking'))

            if room.status.name != 'Available':
                flash(f'Phòng {room.name} hiện không còn trống!', 'warning')
                return redirect(url_for('booking'))

            if num_people > room.capacity:
                flash(f'Số người vượt quá sức chứa ({room.capacity} người)!', 'danger')
                return redirect(url_for('booking'))

            # Tìm hoặc tạo khách hàng
            customer = dao.find_customer_by_phone(customer_phone)
            if customer:
                if customer.full_name != customer_name:
                    dao.update_customer_name(customer, customer_name)
            else:
                customer = dao.create_customer(customer_name, customer_phone)

            # Xác định trạng thái phòng
            time_diff = (start_time - datetime.now()).total_seconds() / 60
            new_status_id = 2 if time_diff <= 30 else 3  # Occupied or Booked

            # Tạo bill
            dao.create_bill(
                customer_id=customer.id,
                room_id=room_id,
                user_id=2,  # Default user
                start_time=start_time,
                status_id=1  # Unpaid
            )

            # Cập nhật trạng thái phòng
            dao.update_room_status(room_id, new_status_id)

            status_text = "đang sử dụng" if new_status_id == 2 else "đã đặt"
            flash(f'✓ Đặt phòng {room.name} thành công! ({status_text})', 'success')

            return redirect(url_for('home'))

        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('booking'))

    # GET - Hiển thị form
    available_rooms = dao.get_available_rooms()
    return render_template('booking.html', rooms=available_rooms)


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


if __name__ == '__main__':
    app.run(debug=True)