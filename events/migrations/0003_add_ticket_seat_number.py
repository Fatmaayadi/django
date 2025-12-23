from django.db import migrations, connection


def add_seat_column(apps, schema_editor):
    table = 'events_ticket'
    column = 'seat_number'
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
        except Exception:
            cols = []
        if column in cols:
            return
        # Add the column (SQLite syntax)
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} varchar(20)")


def noop(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_eventcategory_image"),
    ]

    operations = [
        migrations.RunPython(add_seat_column, reverse_code=noop),
    ]
