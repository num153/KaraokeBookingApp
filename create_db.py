from karaokeapp import app, db
from karaokeapp.models import (
    Role, User, RoomStatus, Room, Customer,
    DiscountPolicy, BillStatus, Bill, Service, BillDetail
)
from datetime import datetime, timedelta


def create_sample_data():

    print("Đang tạo database và tables...")
    with app.app_context():
        # Xóa tất cả tables cũ và tạo mới
        db.drop_all()
        db.create_all()

        print("✓ Đã tạo tables thành công!")

        # 1. Tạo Roles
        print("\n1. Đang tạo Roles...")
        roles = [
            Role(id=1, name='Manager', description='Quản lý toàn bộ hệ thống'),
            Role(id=2, name='Receptionist', description='Lễ tân, đặt phòng và thanh toán'),
            Role(id=3, name='ServiceStaff', description='Nhân viên phục vụ, gọi món')
        ]
        db.session.add_all(roles)
        db.session.commit()
        print("✓ Đã tạo 3 roles")

        # 2. Tạo Users
        print("\n2. Đang tạo Users...")
        users = [
            User(id=1, username='admin', password='123456', full_name='Nguyễn Văn Dũng', role_id=1),
            User(id=2, username='letan01', password='123456', full_name='Lê Thị Tâm', role_id=2),
            User(id=3, username='pv01', password='123456', full_name='Trần Văn Bảo', role_id=3)
        ]
        db.session.add_all(users)
        db.session.commit()
        print("✓ Đã tạo 3 users")

        # 3. Tạo Room Statuses
        print("\n3. Đang tạo Room Statuses...")
        room_statuses = [
            RoomStatus(id=1, name='Available'),
            RoomStatus(id=2, name='Occupied'),
            RoomStatus(id=3, name='Booked')
        ]
        db.session.add_all(room_statuses)
        db.session.commit()
        print("✓ Đã tạo 3 room statuses")

        # 4. Tạo Rooms (12 phòng)
        print("\n4. Đang tạo Rooms...")
        rooms = [
            Room(id=1, name='P01', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=2, name='P02', capacity=10, price_per_hour=150000, status_id=2),
            Room(id=3, name='P03', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=4, name='P04', capacity=15, price_per_hour=200000, status_id=2),
            Room(id=5, name='P05', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=6, name='P06', capacity=15, price_per_hour=200000, status_id=3),
            Room(id=7, name='P07', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=8, name='P08', capacity=15, price_per_hour=200000, status_id=2),
            Room(id=9, name='P09', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=10, name='P10', capacity=10, price_per_hour=150000, status_id=1),
            Room(id=11, name='P11', capacity=15, price_per_hour=200000, status_id=2),
            Room(id=12, name='P12', capacity=10, price_per_hour=150000, status_id=1)
        ]
        db.session.add_all(rooms)
        db.session.commit()
        print("✓ Đã tạo 12 phòng hát")

        # 5. Tạo Customers
        print("\n5. Đang tạo Customers...")
        customers = [
            Customer(id=1, full_name='Nguyễn Văn Huy', phone='0909123456', monthly_visits=12),
            Customer(id=2, full_name='Trần Văn Khôi', phone='0918123456', monthly_visits=2),
            Customer(id=3, full_name='Lê Thị Hoa', phone='0987654321', monthly_visits=8),
            Customer(id=4, full_name='Phạm Minh Tuấn', phone='0912345678', monthly_visits=5),
            Customer(id=5, full_name='Võ Thị Mai', phone='0923456789', monthly_visits=15)
        ]
        db.session.add_all(customers)
        db.session.commit()
        print("✓ Đã tạo 5 khách hàng")

        # 6. Tạo Discount Policies
        print("\n6. Đang tạo Discount Policies...")
        policies = [
            DiscountPolicy(
                id=1,
                name='Khách hàng thân thiết',
                min_visit_req=10,
                discount_percent=5.00,
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 12, 31),
                is_active=True
            ),
            DiscountPolicy(
                id=2,
                name='Khuyến mãi Tết',
                min_visit_req=0,
                discount_percent=10.00,
                start_date=datetime(2025, 1, 15),
                end_date=datetime(2025, 2, 15),
                is_active=False
            )
        ]
        db.session.add_all(policies)
        db.session.commit()
        print("✓ Đã tạo 2 chính sách giảm giá")

        # 7. Tạo Bill Statuses
        print("\n7. Đang tạo Bill Statuses...")
        bill_statuses = [
            BillStatus(id=1, name='Unpaid'),
            BillStatus(id=2, name='Paid')
        ]
        db.session.add_all(bill_statuses)
        db.session.commit()
        print("✓ Đã tạo 2 bill statuses")

        # 8. Tạo Services
        print("\n8. Đang tạo Services...")
        services = [
            Service(id=1, name='Bia Tiger', unit='Lon', price=25000),
            Service(id=2, name='Bia Heineken', unit='Lon', price=30000),
            Service(id=3, name='Trái cây thập cẩm', unit='Dĩa', price=150000),
            Service(id=4, name='Khô bò', unit='Dĩa', price=100000),
            Service(id=5, name='Nước suối', unit='Chai', price=15000),
            Service(id=6, name='Coca Cola', unit='Lon', price=20000),
            Service(id=7, name='Pepsi', unit='Lon', price=20000),
            Service(id=8, name='Snack', unit='Gói', price=25000),
            Service(id=9, name='Mực khô', unit='Dĩa', price=120000),
            Service(id=10, name='Nước cam', unit='Ly', price=35000)
        ]
        db.session.add_all(services)
        db.session.commit()
        print("✓ Đã tạo 10 dịch vụ")

        # 9. Tạo Bills mẫu
        print("\n9. Đang tạo Bills...")
        bills = [
            # Hóa đơn đã thanh toán
            Bill(
                id=1,
                customer_id=1,
                room_id=3,
                user_id=2,
                policy_id=1,
                status_id=2,
                start_time=datetime(2025, 12, 20, 19, 0),
                end_time=datetime(2025, 12, 20, 21, 0),
                total_amount=550000
            ),
            # Hóa đơn đang sử dụng (Phòng P02)
            Bill(
                id=2,
                customer_id=2,
                room_id=2,
                user_id=3,
                policy_id=None,
                status_id=1,
                start_time=datetime.now() - timedelta(hours=1),
                end_time=None,
                total_amount=0
            ),
            # Hóa đơn đang sử dụng (Phòng P04)
            Bill(
                id=3,
                customer_id=3,
                room_id=4,
                user_id=2,
                policy_id=None,
                status_id=1,
                start_time=datetime.now() - timedelta(minutes=30),
                end_time=None,
                total_amount=0
            ),
            # Hóa đơn đang sử dụng (Phòng P08)
            Bill(
                id=4,
                customer_id=4,
                room_id=8,
                user_id=3,
                policy_id=None,
                status_id=1,
                start_time=datetime.now() - timedelta(hours=2),
                end_time=None,
                total_amount=0
            ),
            # Hóa đơn đang sử dụng (Phòng P11)
            Bill(
                id=5,
                customer_id=5,
                room_id=11,
                user_id=2,
                policy_id=1,
                status_id=1,
                start_time=datetime.now() - timedelta(minutes=45),
                end_time=None,
                total_amount=0
            )
        ]
        db.session.add_all(bills)
        db.session.commit()
        print("✓ Đã tạo 5 hóa đơn")

        # 10. Tạo Bill Details
        print("\n10. Đang tạo Bill Details...")
        bill_details = [
            # Hóa đơn 1 (đã thanh toán)
            BillDetail(id=1, bill_id=1, service_id=1, quantity=10, price_at_order=25000),
            BillDetail(id=2, bill_id=1, service_id=3, quantity=1, price_at_order=150000),

            # Hóa đơn 2 (đang sử dụng)
            BillDetail(id=3, bill_id=2, service_id=2, quantity=5, price_at_order=30000),
            BillDetail(id=4, bill_id=2, service_id=5, quantity=3, price_at_order=15000),

            # Hóa đơn 3 (đang sử dụng)
            BillDetail(id=5, bill_id=3, service_id=6, quantity=8, price_at_order=20000),
            BillDetail(id=6, bill_id=3, service_id=8, quantity=4, price_at_order=25000),
        ]
        db.session.add_all(bill_details)
        db.session.commit()
        print("✓ Đã tạo 6 chi tiết hóa đơn")

        print("\n" + "=" * 50)
        print("🎉 TẠO DỮ LIỆU MẪU THÀNH CÔNG!")
        print("=" * 50)
        print("\n📊 Tổng kết:")
        print(f"  - Roles: {Role.query.count()}")
        print(f"  - Users: {User.query.count()}")
        print(f"  - Room Statuses: {RoomStatus.query.count()}")
        print(f"  - Rooms: {Room.query.count()}")
        print(f"  - Customers: {Customer.query.count()}")
        print(f"  - Discount Policies: {DiscountPolicy.query.count()}")
        print(f"  - Bill Statuses: {BillStatus.query.count()}")
        print(f"  - Bills: {Bill.query.count()}")
        print(f"  - Services: {Service.query.count()}")
        print(f"  - Bill Details: {BillDetail.query.count()}")
        print("\n🔐 Tài khoản đăng nhập:")
        print("  - Admin: admin/123456")
        print("  - Lễ tân: letan01/123456")
        print("  - Phục vụ: pv01/123456")
        print("\n✅ Bạn có thể bắt đầu code các chức năng!")


if __name__ == '__main__':
    create_sample_data()