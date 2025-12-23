from django.db import migrations, connection


def add_seat_column(apps, schema_editor):
    # Only run for SQLite (safe fallback). Check if column exists; if not, add it.
    table = 'events_ticket'
    column = 'seat_number'
    with connection.cursor() as cursor:
        # get table info
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            cols = []
        if column in cols:
            return
        # add column
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} varchar(20)")
        except Exception:
            # best-effort; if it fails, let migration error surface
            raise


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0002_eventcategory_image'),
    ]

    operations = [
        migrations.RunPython(add_seat_column, reverse_code=noop),
    ]
