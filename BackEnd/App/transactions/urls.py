from django.urls import path
from . import views

urlpatterns = [
    # Transaction CRUD
    path('', views.TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Statistics
    path('stats/', views.transaction_stats, name='transaction-stats'),
    
    # User transactions
    path('user/', views.user_transactions, name='user-transactions'),
    
    # Create from enrollment
    path('create-from-enrollment/', views.create_transaction_from_enrollment, name='create-transaction-from-enrollment'),
]
