from rest_framework import serializers
from .models import Member
from datetime import date, timedelta

class AttendanceMarkSerializer(serializers.Serializer):
    last_4_digits = serializers.CharField(max_length=4)

# =========================
# #ADD_MEMBER
# =========================
class MemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', 'phone', 'start_date']

    def create(self, validated_data):
        start_date = validated_data['start_date']

        # #AUTO_30_DAYS_MEMBERSHIP
        validated_data['end_date'] = start_date + timedelta(days=30)

        return super().create(validated_data)
# =========================
# #EDIT_MEMBER
# =========================
class MemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', 'phone', 'start_date', 'end_date']
# =========================
# #RENEW_MEMBER
# =========================
class MemberRenewSerializer(serializers.Serializer):
    payment_date = serializers.DateField()

# =========================
# #EDIT_MEMBER
# =========================
class MemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name', 'phone', 'start_date', 'end_date']

# =========================
# #RENEW_MEMBER
# =========================
class MemberRenewSerializer(serializers.Serializer):
    payment_date = serializers.DateField()
