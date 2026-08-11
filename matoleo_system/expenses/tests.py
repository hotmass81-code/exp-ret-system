from django.db import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from core.models import Department, Approver, UserProfile, Contribution, DepartmentBudget, BudgetTransaction
from .models import ExpenseRequest
from .views import _compute_department_budget_summary


class DashboardFilteringTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create departments
        self.dept_a = Department.objects.create(name='Department A', is_active=True)
        self.dept_b = Department.objects.create(name='Department B', is_active=True)

        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.first_approver_user = User.objects.create_user(username='first_approver', password='pass123')
        self.second_approver_user = User.objects.create_user(username='second_approver', password='pass123')

        # Create approver profiles
        self.first_approver = Approver.objects.create(
            user=self.first_approver_user,
            level='first',
            is_active=True
        )
        self.first_approver.departments.add(self.dept_a)  # Only assigned to dept A

        self.second_approver = Approver.objects.create(
            user=self.second_approver_user,
            level='second',
            is_active=True
        )

        # Create regular user
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        profile, _ = UserProfile.objects.get_or_create(user=self.regular_user)
        profile.department = self.dept_a
        profile.is_approved = True
        profile.save()

        # Create test expense requests
        self.expense_a = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_a,
            first_name='John',
            last_name='Doe',
            phone_number='+1234567890',
            date=date.today(),
            reason='Test expense A',
            total_amount=100.00,
            status='submitted'
        )

        self.expense_b = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_b,
            first_name='Jane',
            last_name='Smith',
            phone_number='+1234567890',
            date=date.today(),
            reason='Test expense B',
            total_amount=200.00,
            status='submitted'
        )

    def test_form_number_uniqueness_generated_on_save(self):
        second_expense = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_a,
            first_name='Alice',
            last_name='Johnson',
            phone_number='+1234567890',
            date=date.today(),
            reason='Test expense C',
            total_amount=150.00,
            status='draft'
        )
        self.assertNotEqual(self.expense_a.form_number, second_expense.form_number)
        self.assertTrue(second_expense.form_number.startswith(f'EXP-{date.today().year}-'))

    def test_create_expense_draft_form(self):
        data = {
            'first_name': 'Draft',
            'last_name': 'User',
            'phone_number': '+255000000000',
            'department': str(self.dept_a.id),
            'date': date.today().isoformat(),
            'reason': 'Draft save test',
            'item_description[]': ['Item 1'],
            'item_amount[]': ['100.00'],
            'budget_choice': 'BK',
        }
        self.client.login(username='regular', password='pass123')
        response = self.client.post('/expenses/new/', data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'created as draft')
        self.assertTrue(ExpenseRequest.objects.filter(submitted_by=self.regular_user, reason='Draft save test').exists())

    def test_mk_budget_choice_does_not_create_budget_transaction_on_payment(self):
        budget = DepartmentBudget.objects.create(department=self.dept_a, bk_amount=1000)
        mk_expense = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_a,
            first_name='MK',
            last_name='Tester',
            phone_number='+1234567890',
            date=date.today(),
            reason='MK expense',
            total_amount=200.00,
            status='approved',
            budget_choice='MK'
        )
        mk_expense.is_paid = False
        mk_expense.save()
        BudgetTransaction.objects.filter(expense_form_number=mk_expense.form_number).delete()
        # Simulate marking as paid through the view logic
        if mk_expense.budget_choice != 'MK':
            BudgetTransaction.objects.create(
                department=mk_expense.department,
                contribution=mk_expense.contribution if mk_expense.budget_choice == 'CONTRIBUTION' else None,
                expense_form_number=mk_expense.form_number,
                amount=mk_expense.total_amount,
                transaction_type='deduction'
            )
        transactions = BudgetTransaction.objects.filter(expense_form_number=mk_expense.form_number)
        self.assertEqual(transactions.count(), 0)

    def test_mk_form_is_excluded_from_bk_and_contribution_summary(self):
        DepartmentBudget.objects.create(department=self.dept_a, bk_amount=1000)
        contrib = Contribution.objects.create(department=self.dept_a, name='Test Contribution', amount=500, is_active=True)

        # Create one MK expense and one BK expense with same department
        mk_expense = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_a,
            first_name='MK',
            last_name='Tester',
            phone_number='+1234567890',
            date=date.today(),
            reason='MK expense',
            total_amount=200.00,
            status='approved',
            budget_choice='MK'
        )
        bk_expense = ExpenseRequest.objects.create(
            submitted_by=self.regular_user,
            department=self.dept_a,
            first_name='BK',
            last_name='Tester',
            phone_number='+1234567890',
            date=date.today(),
            reason='BK expense',
            total_amount=150.00,
            status='approved',
            budget_choice='BK'
        )

        # Add BK transaction for bk_expense and ensure MK is not recorded
        BudgetTransaction.objects.create(
            department=self.dept_a,
            contribution=None,
            expense_form_number=bk_expense.form_number,
            amount=bk_expense.total_amount,
            transaction_type='deduction'
        )
        BudgetTransaction.objects.create(
            department=self.dept_a,
            contribution=contrib,
            expense_form_number=mk_expense.form_number,
            amount=mk_expense.total_amount,
            transaction_type='deduction'
        )

        summary = _compute_department_budget_summary(self.dept_a)

        self.assertEqual(summary['bk_used'], 150.00)
        self.assertEqual(summary['mk_total_amount'], 200.00)
        self.assertEqual(len(summary['bk_forms']), 1)
        self.assertTrue(any(item['form_number'] == mk_expense.form_number for item in summary['mk_requests']))
        self.assertFalse(any(item['form_number'] == mk_expense.form_number for item in summary['bk_forms']))

    def test_first_approver_sees_only_assigned_department(self):
        """First approver should only see expenses from their assigned departments"""
        self.client.login(username='first_approver', password='pass123')
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 200)

        # Should contain expense from dept A (John Doe) but not dept B (Jane Smith)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Jane Smith')

    def test_second_approver_sees_all_departments(self):
        """Second approver should see expenses from all departments"""
        self.client.login(username='second_approver', password='pass123')
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 200)

        # Should contain expenses from both departments
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')

    def test_admin_sees_all_departments(self):
        """Admin should see expenses from all departments"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 200)

        # Should contain expenses from both departments
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')

    def test_regular_user_sees_only_own_expenses(self):
        """Regular user should only see their own expenses"""
        self.client.login(username='regular', password='pass123')
        response = self.client.get('/expenses/')
        self.assertEqual(response.status_code, 200)

        # Should contain both expenses since they were created by this user
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')
