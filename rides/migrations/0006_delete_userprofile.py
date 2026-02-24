from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('rides', '0005_alter_riderequest_seats_requested_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
