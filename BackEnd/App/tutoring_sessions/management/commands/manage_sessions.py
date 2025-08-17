from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from tutoring_sessions.models import Session, SessionStatus


class Command(BaseCommand):
    help = 'Manage session lifecycle: expire old sessions, archive completed ones, and optimize performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--expire',
            action='store_true',
            help='Expire sessions that are past their end time',
        )
        parser.add_argument(
            '--archive',
            action='store_true',
            help='Archive completed sessions older than 30 days',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up expired sessions and optimize database',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all management operations',
        )

    def handle(self, *args, **options):
        if options['all'] or options['expire']:
            self.expire_sessions()

        if options['all'] or options['archive']:
            self.archive_sessions()

        if options['all'] or options['cleanup']:
            self.cleanup_sessions()

    def expire_sessions(self):
        """Expire sessions that are past their end time"""
        self.stdout.write("🕐 Checking for sessions to expire...")

        expired_count = 0
        with transaction.atomic():
            # Get sessions that should be expired
            sessions_to_expire = Session.objects.filter(
                status__in=['pending_approval',
                            'approved', 'scheduled', 'live']
            ).select_related('status_tracker')

            for session in sessions_to_expire:
                if session.should_be_expired:
                    # Update session status
                    session.status = 'expired'
                    session.save()

                    # Update status tracker
                    try:
                        status_tracker = session.status_tracker
                        status_tracker.update_status(
                            'expired', 'Auto-expired by management command')
                        status_tracker.is_active = False
                        status_tracker.save()
                    except SessionStatus.DoesNotExist:
                        pass

                    expired_count += 1
                    self.stdout.write(
                        f"  ✅ Expired: {session.title} (ID: {session.id})")

        self.stdout.write(
            self.style.SUCCESS(f"🎯 Expired {expired_count} sessions")
        )

    def archive_sessions(self):
        """Archive completed sessions older than 30 days"""
        self.stdout.write("📦 Checking for sessions to archive...")

        archive_threshold = timezone.now() - timedelta(days=30)
        archived_count = 0

        with transaction.atomic():
            # Get completed sessions older than 30 days
            sessions_to_archive = Session.objects.filter(
                status='completed',
                ended_at__lt=archive_threshold
            ).select_related('status_tracker')

            for session in sessions_to_archive:
                # Update session status
                session.status = 'archived'
                session.save()

                # Update status tracker
                try:
                    status_tracker = session.status_tracker
                    status_tracker.update_status(
                        'archived', 'Auto-archived by management command')
                    status_tracker.is_active = False
                    status_tracker.should_archive = True
                    status_tracker.archive_date = timezone.now()
                    status_tracker.save()
                except SessionStatus.DoesNotExist:
                    pass

                archived_count += 1
                self.stdout.write(
                    f"  📦 Archived: {session.title} (ID: {session.id})")

        self.stdout.write(
            self.style.SUCCESS(f"📦 Archived {archived_count} sessions")
        )

    def cleanup_sessions(self):
        """Clean up expired sessions and optimize database"""
        self.stdout.write("🧹 Cleaning up sessions...")

        # Count sessions by status
        status_counts = {}
        for status, _ in Session.STATUS_CHOICES:
            count = Session.objects.filter(status=status).count()
            status_counts[status] = count

        # Show current status distribution
        self.stdout.write("📊 Current session status distribution:")
        for status, count in status_counts.items():
            if count > 0:
                self.stdout.write(f"  {status}: {count}")

        # Optimize status trackers
        optimized_count = 0
        with transaction.atomic():
            # Clean up status history for old sessions
            status_trackers = SessionStatus.objects.filter(
                session__status__in=['expired', 'archived']
            )

            for tracker in status_trackers:
                # Keep only last 5 status changes for archived sessions
                if len(tracker.status_history) > 5:
                    tracker.status_history = tracker.status_history[-5:]
                    tracker.save()
                    optimized_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"🧹 Optimized {optimized_count} status trackers")
        )

    def show_statistics(self):
        """Show session statistics"""
        self.stdout.write("📈 Session Statistics:")

        total_sessions = Session.objects.count()
        active_sessions = Session.objects.filter(
            status__in=['pending_approval', 'approved', 'scheduled', 'live']).count()
        completed_sessions = Session.objects.filter(status='completed').count()
        expired_sessions = Session.objects.filter(status='expired').count()
        archived_sessions = Session.objects.filter(status='archived').count()

        self.stdout.write(f"  Total Sessions: {total_sessions}")
        self.stdout.write(f"  Active Sessions: {active_sessions}")
        self.stdout.write(f"  Completed Sessions: {completed_sessions}")
        self.stdout.write(f"  Expired Sessions: {expired_sessions}")
        self.stdout.write(f"  Archived Sessions: {archived_sessions}")

