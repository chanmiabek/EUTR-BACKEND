from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from members.models import MemberProfile
from posts.models import Post
from volunteering.models import Opportunity
from donations.models import Donation
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed sample data for Educate Us, Rise Us'

    def handle(self, *args, **options):
        User = get_user_model()

        admin_user, _ = User.objects.get_or_create(
            email='admin@example.com',
            defaults={'full_name': 'Admin User', 'is_staff': True, 'is_superuser': True}
        )
        if not admin_user.has_usable_password():
            admin_user.set_password('admin1234')
            admin_user.save()

        user1, _ = User.objects.get_or_create(
            email='member1@example.com',
            defaults={'full_name': 'Community Member One'}
        )
        if not user1.has_usable_password():
            user1.set_password('password123')
            user1.save()

        user2, _ = User.objects.get_or_create(
            email='member2@example.com',
            defaults={'full_name': 'Community Member Two'}
        )
        if not user2.has_usable_password():
            user2.set_password('password123')
            user2.save()

        MemberProfile.objects.get_or_create(user=user1, defaults={
            'bio': 'Focused on education and youth empowerment.',
            'location': 'Kakuma',
            'skills': 'Teaching, Mentorship',
        })
        MemberProfile.objects.get_or_create(user=user2, defaults={
            'bio': 'Community organizer and volunteer coordinator.',
            'location': 'Kakuma',
            'skills': 'Leadership, Events',
        })

        Post.objects.get_or_create(
            title='Welcome to Educate Us, Rise Us',
            defaults={'content': 'Our community is building pathways to education and opportunity.', 'author': admin_user}
        )
        Post.objects.get_or_create(
            title='Volunteer Spotlight',
            defaults={'content': 'Meet the volunteers making a difference this month.', 'author': admin_user}
        )

        Opportunity.objects.get_or_create(
            title='Youth Mentorship Program',
            defaults={'description': 'Support youth with weekly mentorship sessions.', 'location': 'Kakuma', 'is_active': True}
        )
        Opportunity.objects.get_or_create(
            title='Community Clean-up Day',
            defaults={'description': 'Join us for a community clean-up and awareness drive.', 'location': 'Kakuma', 'is_active': True}
        )

        Donation.objects.get_or_create(
            donor_name='Anonymous',
            email='anon@example.com',
            defaults={
                'amount': 5000,
                'currency': 'KES',
                'payment_method': 'mpesa',
                'status': 'completed',
                'created_at': timezone.now(),
            }
        )

        self.stdout.write(self.style.SUCCESS('Seed data created/updated.'))
