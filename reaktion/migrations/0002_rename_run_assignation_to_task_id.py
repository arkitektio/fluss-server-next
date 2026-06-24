from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reaktion", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="run",
            old_name="assignation",
            new_name="task_id",
        ),
    ]
