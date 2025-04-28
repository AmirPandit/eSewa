from django.core.management.base import BaseCommand
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

class Command(BaseCommand):
    help = 'Syncs the Cassandra keyspace'

    def handle(self, *args, **kwargs):
        cluster = Cluster(['cassandra'])  # Connect to the Cassandra container
        session = cluster.connect()

        # Create keyspace if it doesn't exist
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS chat_keyspace 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
        """)

        self.stdout.write(self.style.SUCCESS('Successfully synced Cassandra keyspace'))
