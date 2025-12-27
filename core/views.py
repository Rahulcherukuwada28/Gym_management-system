from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from datetime import timedelta, date, time
from django.utils import timezone
from django.db.models.functions import TruncDate

from .models import Member, GymConfig, Attendance
from .serializers import (
    MemberCreateSerializer,
    MemberUpdateSerializer,
    MemberRenewSerializer,
    AttendanceMarkSerializer,
)
from .utils import get_member_status


# BASE OWNER VIEW
class OwnerAPIView(APIView):
    permission_classes = [IsAuthenticated]

# QR ATTENDANCE (PUBLIC)
class MarkAttendanceView(APIView):
    def post(self, request):
        serializer = AttendanceMarkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        last_4 = serializer.validated_data["last_4_digits"]

        config = GymConfig.objects.first()
        if not config or not config.qr_active:
            return Response({"message": "QR attendance disabled"}, status=403)

        now = timezone.localtime().time()
        if not (time(5, 0) <= now <= time(23, 0)):
            return Response(
                {"message": "Attendance allowed only between 5 AM and 11 PM"},
                status=403,
            )

        members = Member.objects.filter(phone__endswith=last_4, is_active=True)
        if not members.exists():
            return Response({"message": "Member not found"}, status=404)
        if members.count() > 1:
            return Response(
                {"message": "Multiple members found. Contact owner."}, status=400
            )

        member = members.first()
        today = timezone.localdate()

        attendance, created = Attendance.objects.get_or_create(
            member=member,
            date=today,   # ✅ SINGLE SOURCE OF TRUTH
        )

        if not created:
            return Response({"message": "Attendance already marked"}, status=200)

        status_text, color = get_member_status(
            member, grace_days=config.grace_days
        )

        return Response(
            {
                "message": "Attendance marked successfully",
                "name": member.name,
                "status": status_text,
                "color": color,
                "expiry_date": member.end_date,
            },
            status=201,
        )

# MEMBERS (LIST + CREATE + SOFT DELETE)
class MembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        members = Member.objects.filter(is_active=True).order_by("-id")
        return Response(
            {
                "count": members.count(),
                "members": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "phone": m.phone,
                        "start_date": m.start_date,
                        "end_date": m.end_date,
                    }
                    for m in members
                ],
            },
            status=200,
        )

    def post(self, request):
        serializer = MemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

        return Response(
            {
                "message": "Member added successfully",
                "id": member.id,
                "name": member.name,
                "end_date": member.end_date,
            },
            status=201,
        )

    def delete(self, request, id):
        try:
            member = Member.objects.get(id=id, is_active=True)
        except Member.DoesNotExist:
            return Response({"message": "Member not found"}, status=404)

        member.is_active = False
        member.save()
        return Response({"message": "Member archived successfully"}, status=200)


# EDIT MEMBER
class EditMemberView(OwnerAPIView):
    def put(self, request, id):
        try:
            member = Member.objects.get(id=id, is_active=True)
        except Member.DoesNotExist:
            return Response({"message": "Member not found"}, status=404)

        serializer = MemberUpdateSerializer(member, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Member updated successfully"}, status=200)

# RENEW MEMBER (BALANCED LOGIC)
class RenewMemberView(OwnerAPIView):
    def post(self, request, id):
        serializer = MemberRenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_date = serializer.validated_data['payment_date']

        try:
            member = Member.objects.get(id=id, is_active=True)
        except Member.DoesNotExist:
            return Response({"message": "Member not found"}, status=404)

        config = GymConfig.objects.first()
        grace_days = config.grace_days if config else 4

        last_expiry = member.end_date

        # GAP = how late the payment is
        gap_days = (payment_date - last_expiry).days

        # 🔴 RULE: Large gap → START FRESH
        if gap_days > 15:
            new_end_date = payment_date + timedelta(days=30)

        # 🟡 RULE: Small gap / within grace → EXTEND
        else:
            # If expired but within grace or short delay
            if payment_date > last_expiry:
                new_end_date = last_expiry + timedelta(days=30)
            else:
                # Renewed early
                new_end_date = last_expiry + timedelta(days=30)

        member.end_date = new_end_date
        member.save()

        return Response({
            "message": "Membership renewed successfully",
            "new_end_date": new_end_date,
            "gap_days": max(gap_days, 0)
        }, status=200)


# DASHBOARD SUMMARY
class DashboardSummaryView(OwnerAPIView):
    def get(self, request):
        today = timezone.localdate()
        grace_days = 4
        grace_start = today - timedelta(days=grace_days)

        base_qs = Member.objects.filter(is_active=True)

        def pack(qs):
            return {
                "count": qs.count(),
                "names": [
                    {"id": m.id, "name": m.name, "end_date": m.end_date}
                    for m in qs.order_by("end_date")[:5]
                ],
            }

        visits = Attendance.objects.filter(date=today).select_related("member")

        return Response(
            {
                "active_members": pack(base_qs.filter(end_date__gte=today)),
                "grace_members": pack(
                    base_qs.filter(end_date__lt=today, end_date__gte=grace_start)
                ),
                "expired_members": pack(base_qs.filter(end_date__lt=grace_start)),
                "today_visits": {
                    "count": visits.count(),
                    "names": [
                        {
                            "id": v.member.id,
                            "name": v.member.name,
                            "end_date": v.member.end_date,
                        }
                        for v in visits
                    ],
                },
            }
        )


# ARCHIVED MEMBERS
class ArchivedMembersView(OwnerAPIView):
    def get(self, request):
        members = Member.objects.filter(is_active=False).order_by("-id")
        return Response(
            {
                "count": members.count(),
                "members": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "phone": m.phone,
                        "start_date": m.start_date,
                        "end_date": m.end_date,
                    }
                    for m in members
                ],
            },
            status=200,
        )


class RestoreMemberView(OwnerAPIView):
    def post(self, request, id):
        try:
            member = Member.objects.get(id=id, is_active=False)
        except Member.DoesNotExist:
            return Response({"message": "Archived member not found"}, status=404)

        member.is_active = True
        member.save()
        return Response({"message": "Member restored successfully"}, status=200)


class PermanentDeleteMemberView(OwnerAPIView):
    def delete(self, request, id):
        try:
            member = Member.objects.get(id=id, is_active=False)
        except Member.DoesNotExist:
            return Response({"message": "Archived member not found"}, status=404)

        member.delete()
        return Response({"message": "Member permanently deleted"}, status=200)


# ATTENDANCE HISTORY
class MemberAttendanceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            member = Member.objects.get(id=id)

            # ✅ Joining date (safe)
            joining_date = (
                member.joining_date
                if hasattr(member, "joining_date") and member.joining_date
                else member.created_at.date()
            )

            # ✅ Attendance dates (timezone safe, date-only)
            present_dates_qs = (
                Attendance.objects
                .filter(member=member)
                .annotate(day=TruncDate("created_at"))
                .values_list("day", flat=True)
                .distinct()
            )

            return Response({
                "joining_date": joining_date.strftime("%Y-%m-%d"),
                "present_dates": [
                    d.strftime("%Y-%m-%d") for d in present_dates_qs
                ]
            })

        except Member.DoesNotExist:
            return Response(
                {"error": "Member not found"},
                status=404
            )