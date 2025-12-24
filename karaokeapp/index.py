from decimal import Decimal

from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
from datetime import datetime, date

from karaokeapp import app, db
from karaokeapp import dao
from karaokeapp.models import Room, Bill, Customer, RoomStatus, BillDetail


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
            new_status_id = 2 if time_diff <= 30 else 3 #nếu bé hơn 30 phút mới tính là đang sử dụng
            # Tạo bill
            dao.create_bill(
                customer_id=customer.id,
                room_id=room_id,
                user_id=2,  # Default user
                start_time=start_time,
                status_id=1  # Unpaid
            )

            dao.update_room_status(room_id, new_status_id)
            db.session.commit()

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
    """Trang quản lý dịch vụ"""
    # Lấy tất cả phòng đang hoạt động (Occupied)
    active_bills = Bill.query \
        .filter_by(status_id=1) \
        .join(Room) \
        .filter(Room.status_id == 2) \
        .order_by(Room.name) \
        .all()

    # Tính số lượng dịch vụ hiện tại của mỗi phòng
    active_rooms = []
    for bill in active_bills:
        service_count = BillDetail.query.filter_by(bill_id=bill.id).count()
        active_rooms.append({
            'room': bill.room,
            'bill': bill,
            'current_services_count': service_count
        })

    # Lấy tất cả dịch vụ
    all_services = dao.get_all_services()

    return render_template('services.html',
                           active_rooms=active_rooms,
                           services=all_services)


@app.route('/api/bill/<int:bill_id>/services')
def api_get_bill_services(bill_id):
    """API: Lấy danh sách dịch vụ của bill"""
    from decimal import Decimal

    try:
        bill_details = dao.get_bill_details(bill_id)

        services = []
        total = Decimal('0')

        for detail in bill_details:
            item_total = Decimal(str(detail.quantity)) * detail.price_at_order
            services.append({
                'detail_id': detail.id,
                'service_id': detail.service.id,
                'name': detail.service.name,
                'unit': detail.service.unit,
                'quantity': detail.quantity,
                'price': float(detail.price_at_order),
                'total': float(item_total)
            })
            total += item_total

        return jsonify({
            'success': True,
            'services': services,
            'total': float(total)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/api/bill/add-service', methods=['POST'])
def api_add_service():
    """API: Thêm dịch vụ vào bill"""
    try:
        data = request.get_json()
        bill_id = data.get('bill_id')
        service_id = data.get('service_id')
        quantity = data.get('quantity', 1)

        if not bill_id or not service_id:
            return jsonify({
                'success': False,
                'message': 'Thiếu thông tin bill_id hoặc service_id'
            }), 400

        # Kiểm tra bill có tồn tại không
        bill = dao.get_bill_by_id(bill_id)
        if not bill:
            return jsonify({
                'success': False,
                'message': 'Hóa đơn không tồn tại'
            }), 404

        # Kiểm tra bill đã thanh toán chưa
        if bill.status_id == 2:
            return jsonify({
                'success': False,
                'message': 'Hóa đơn đã thanh toán, không thể thêm dịch vụ'
            }), 400

        # Thêm dịch vụ
        success = dao.add_service_to_bill(bill_id, service_id, quantity)

        if success:
            return jsonify({
                'success': True,
                'message': 'Thêm dịch vụ thành công'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Không thể thêm dịch vụ'
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/bill/remove-service/<int:detail_id>', methods=['DELETE'])
def api_remove_service(detail_id):
    """API: Xóa dịch vụ khỏi bill"""
    try:
        # Kiểm tra detail có tồn tại không
        detail = BillDetail.query.get(detail_id)
        if not detail:
            return jsonify({
                'success': False,
                'message': 'Dịch vụ không tồn tại'
            }), 404

        # Kiểm tra bill đã thanh toán chưa
        if detail.bill.status_id == 2:
            return jsonify({
                'success': False,
                'message': 'Hóa đơn đã thanh toán, không thể xóa dịch vụ'
            }), 400

        # Xóa dịch vụ
        success = dao.remove_service_from_bill(detail_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Đã xóa dịch vụ'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Không thể xóa dịch vụ'
            }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/bill/<int:bill_id>/service-count')
def api_get_service_count(bill_id):
    """API: Lấy số lượng dịch vụ của bill"""
    try:
        count = BillDetail.query.filter_by(bill_id=bill_id).count()
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/api/services/search')
def api_search_services():
    """API: Tìm kiếm dịch vụ"""
    keyword = request.args.get('q', '')

    try:
        if keyword:
            services = dao.search_services(keyword)
        else:
            services = dao.get_all_services()

        result = [{
            'id': s.id,
            'name': s.name,
            'category': s.category,
            'unit': s.unit,
            'price': float(s.price)
        } for s in services]

        return jsonify({
            'success': True,
            'services': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@app.route('/api/room/<int:room_id>/current-bill')
def api_get_room_current_bill(room_id):
    """API: Lấy bill hiện tại của phòng"""
    try:
        bill = dao.get_active_bill_by_room(room_id)

        if not bill:
            return jsonify({
                'success': False,
                'message': 'Phòng không có bill đang hoạt động'
            }), 404

        return jsonify({
            'success': True,
            'bill_id': bill.id,
            'customer_name': bill.customer.full_name,
            'start_time': bill.start_time.strftime('%H:%M %d/%m/%Y')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# ==================== THANH TOÁN ====================
@app.route('/payment')
def payment_list():
    """Hiển thị danh sách phòng đang sử dụng"""
    # Lấy tất cả bill đang active (Unpaid) và phòng đang sử dụng
    active_bills = Bill.query \
        .filter_by(status_id=1) \
        .join(Room) \
        .filter(Room.status_id == 2) \
        .order_by(Room.name) \
        .all()

    # Tính toán thông tin cho mỗi bill (dùng function chung)
    bills_info = []
    for bill in active_bills:
        info = dao.calculate_bill_info(bill.id)
        if info:
            bills_info.append(info)

    return render_template('payment.html', bills_info=bills_info)


@app.route('/payment/detail/<int:bill_id>')
def payment_detail(bill_id):
    """Xem chi tiết hóa đơn trước khi thanh toán"""
    # Tính toán thông tin (dùng function chung)
    info = dao.calculate_bill_info(bill_id)

    if not info:
        flash('Hóa đơn không tồn tại!', 'danger')
        return redirect(url_for('payment_list'))

    # Lấy chi tiết dịch vụ
    bill_details = dao.get_bill_details(bill_id)

    return render_template('payment_detail.html',
                           bill=info['bill'],
                           bill_details=bill_details,
                           time_used=info['time_used'],
                           room_price=info['room_price'],
                           service_total=info['service_total'],
                           discount=info['discount'],
                           discount_policy=info['discount_policy'],
                           total=info['total'])


@app.route('/payment/process/<int:bill_id>', methods=['POST'])
def process_payment(bill_id):
    """Xử lý thanh toán"""
    try:
        bill = dao.get_bill_by_id(bill_id)
        if not bill:
            flash('Hóa đơn không tồn tại!', 'danger')
            return redirect(url_for('payment_list'))

        if bill.status_id == 2:
            flash('Hóa đơn đã được thanh toán!', 'warning')
            return redirect(url_for('payment_list'))

        # Cập nhật thời gian kết thúc
        bill.end_time = datetime.now()

        # Áp dụng policy nếu khách hàng đủ điều kiện
        if bill.customer:
            policy = dao.check_customer_discount_eligibility(bill.customer.id)
            if policy:
                bill.policy_id = policy.id

        # Tính tổng tiền (function này sẽ update bill.total_amount)
        total = dao.calculate_bill_total(bill_id)

        # Cập nhật trạng thái bill
        bill.status_id = 2  # Paid

        # Cập nhật trạng thái phòng về Available
        dao.update_room_status(bill.room_id, 1)

        # Tăng số lượt đến của khách hàng
        if bill.customer_id:
            dao.increase_customer_visits(bill.customer_id)

        db.session.commit()

        flash(f'✓ Thanh toán thành công! Phòng {bill.room.name} - Tổng tiền: {total:,.0f}đ', 'success')
        return redirect(url_for('home'))

    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {str(e)}")
        flash(f'Lỗi thanh toán: {str(e)}', 'danger')
        return redirect(url_for('payment_list'))


# ==================== BÁO CÁO ====================
@app.route('/reports')
def reports():
    # Logic báo cáo
    pass


if __name__ == '__main__':
    app.run(debug=True)