from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model


class ReportDownloadTests(TestCase):
	def setUp(self):
		User = get_user_model()
		# Create a treasurer user
		self.treasurer = User.objects.create_user(username='treasurer', password='pass')
		# Give treasurer a treasurer_profile if model exists; fallback: make staff
		try:
			from accounts.models import TreasurerProfile
			TreasurerProfile.objects.create(user=self.treasurer)
		except Exception:
			self.treasurer.is_staff = True
			self.treasurer.save()

		# Create a normal user
		self.user = User.objects.create_user(username='normal', password='pass')

		self.client = Client()

	def test_expense_excel_for_treasurer(self):
		self.client.login(username='treasurer', password='pass')
		url = reverse('reports:download_expenses') if 'reports:download_expenses' in [r.name for r in __import__('django.urls').urls.resolver.get_resolver().reverse_dict] else '/reports/download/expenses/'
		resp = self.client.get(url, {'format': 'excel'})
		self.assertEqual(resp.status_code, 200)
		self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resp['Content-Type'])

	def test_retirement_excel_for_treasurer(self):
		self.client.login(username='treasurer', password='pass')
		url = reverse('reports:download_retirement') if 'reports:download_retirement' in [r.name for r in __import__('django.urls').urls.resolver.get_resolver().reverse_dict] else '/reports/download/retirement/'
		resp = self.client.get(url, {'format': 'excel'})
		self.assertEqual(resp.status_code, 200)
		self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resp['Content-Type'])

