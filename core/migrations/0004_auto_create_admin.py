from django.db import migrations

def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', '123')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_order_options'),
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
