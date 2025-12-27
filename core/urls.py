from django.urls import path
from .views import (
    MembersView,
    DashboardSummaryView,
    EditMemberView,
    RenewMemberView,
    ArchivedMembersView,
    MarkAttendanceView,
    RestoreMemberView,
    PermanentDeleteMemberView,
    MemberAttendanceHistoryView
)


urlpatterns = [
    path('members/', MembersView.as_view()),          # GET, POST
    path('members/<int:id>/', MembersView.as_view()), # DELETE (SOFT)
    path('members/archived/', ArchivedMembersView.as_view()),
    path('members/<int:id>/restore/', RestoreMemberView.as_view()),
    path('members/<int:id>/permanent-delete/', PermanentDeleteMemberView.as_view()),


    path('members/<int:id>/edit/', EditMemberView.as_view()),
    path('members/<int:id>/renew/', RenewMemberView.as_view()),

    path('dashboard/summary/', DashboardSummaryView.as_view()),
    path('attendance/mark/', MarkAttendanceView.as_view()),

    path('members/<int:id>/attendance-history/',MemberAttendanceHistoryView.as_view())
]

