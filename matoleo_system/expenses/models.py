from django.db import IntegrityError, models
from django.contrib.auth.models import User
from core.models import Department


class ExpenseRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('first_approved', 'First Approved'),
        ('second_approved', 'Second Approved'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Not Approved'),
        ('rejected_for_editing', 'Rejected for Editing'),
    ]

    form_number = models.CharField(max_length=30, unique=True, blank=True)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_requests')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    reason = models.TextField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # Budgeting fields
    BUDGET_CHOICES = [
        ('BK', 'BK'),
        ('CONTRIBUTION', 'Contribution'),
        ('MK', 'MK'),
    ]
    budget_choice = models.CharField(max_length=20, choices=BUDGET_CHOICES, default='BK')
    contribution = models.ForeignKey('core.Contribution', on_delete=models.SET_NULL, null=True, blank=True)
    budget_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Approval tracking
    first_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='first_approved_expenses')
    first_approver_name = models.CharField(max_length=200, blank=True)
    first_approver_phone = models.CharField(max_length=20, blank=True)
    first_approved_at = models.DateTimeField(null=True, blank=True)
    
    second_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='second_approved_expenses')
    second_approver_name = models.CharField(max_length=200, blank=True)
    second_approver_phone = models.CharField(max_length=20, blank=True)
    second_approved_at = models.DateTimeField(null=True, blank=True)
    
    treasurer_name = models.CharField(max_length=200, blank=True)
    treasurer_phone = models.CharField(max_length=20, blank=True)
    treasurer_approved_at = models.DateTimeField(null=True, blank=True)
    
    admin_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='admin_approved_expenses')
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='paid_expenses')

    payment_method = models.CharField(max_length=50, blank=True, choices=[
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('mpesa', 'M-Pesa'),
    ])
    payment_date = models.DateField(null=True, blank=True)
    reference_number = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Expense Request #{self.form_number} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.form_number:
            import datetime
            year = datetime.date.today().year
            prefix = f"EXP-{year}-"
            existing = ExpenseRequest.objects.filter(form_number__startswith=prefix).values_list('form_number', flat=True)
            max_count = 0
            for form in existing:
                try:
                    count_part = int(form.rsplit('-', 1)[-1])
                    if count_part > max_count:
                        max_count = count_part
                except (IndexError, ValueError):
                    continue
            count = max_count + 1

            while count <= 9999:
                self.form_number = f"{prefix}{count:04d}"
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    count += 1
            raise IntegrityError('Unable to generate a unique ExpenseRequest form_number.')
        super().save(*args, **kwargs)

    def get_approval_ticks(self):
        if self.status == 'approved':
            return 'approved'
        elif self.status == 'rejected':
            return 'rejected'
        elif self.status == 'second_approved':
            return 'two_ticks'
        elif self.status == 'first_approved':
            return 'one_tick'
        return 'none'

    def can_edit(self):
        return self.status in ['draft', 'rejected_for_editing']
    
    def get_approval_status(self):
        """Return detailed approval status for display"""
        statuses = {
            'first_approver': self.first_approved_at is not None,
            'second_approver': self.second_approved_at is not None,
        }
        return statuses


class ExpenseItem(models.Model):
    expense_request = models.ForeignKey(ExpenseRequest, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.description}: {self.amount}"
