from django.db import models


from django.db import models


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ("Network", "Network"),
        ("Hardware", "Hardware"),
        ("Software", "Software"),
        ("Other", "Other"),
    ]

    URGENCY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
    ]

    id = models.CharField(
        primary_key=True,
        max_length=10,
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
    )
    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
    )
    affected_users = models.PositiveIntegerField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="low",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )
    assigned_to = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
