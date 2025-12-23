from django.db import migrations


def add_seat_number_column(apps, schema_editor):
    table_name = "events_ticket"
    conn = schema_editor.connection
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = [row[1] for row in cursor.fetchall()]
    if "seat_number" in cols:
        return
    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN seat_number varchar(20);")


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_seat_number_column, reverse_code=migrations.RunPython.noop),
    ]
