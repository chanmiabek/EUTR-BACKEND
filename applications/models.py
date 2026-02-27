from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedActiveModel(TimeStampedModel):
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Application(TimeStampedModel):
    TYPE_VOLUNTEER = "volunteer"
    TYPE_JOIN = "join"
    TYPE_CHOICES = [
        (TYPE_VOLUNTEER, "Volunteer"),
        (TYPE_JOIN, "Join Us"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=120, blank=True)
    availability = models.CharField(max_length=120, blank=True)
    preferred_start_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_applications",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type}: {self.name} <{self.email}>"


class Program(OrderedActiveModel):
    title = models.CharField(max_length=200)
    focus = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=80, default="Active")
    beneficiaries = models.CharField(max_length=200, blank=True)
    highlights = models.JSONField(default=list, blank=True)
    image = models.URLField(blank=True)
    photo = models.ImageField(upload_to="programs/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class Project(OrderedActiveModel):
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=80, blank=True)
    copy = models.TextField()
    image = models.URLField(blank=True)
    photo = models.ImageField(upload_to="projects/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.title


class Event(OrderedActiveModel):
    title = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    tag = models.CharField(max_length=80, blank=True)
    description = models.TextField()
    highlights = models.JSONField(default=list, blank=True)
    image = models.URLField(blank=True)
    photo = models.ImageField(upload_to="events/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "date", "id"]

    def __str__(self):
        return self.title


class TeamMember(OrderedActiveModel):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    copy = models.TextField(blank=True)
    image = models.URLField(blank=True)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class Partner(OrderedActiveModel):
    name = models.CharField(max_length=120)
    link = models.URLField(blank=True)
    logo = models.ImageField(upload_to="partners/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class Testimonial(OrderedActiveModel):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    quote = models.TextField()
    image = models.URLField(blank=True)
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.name}"


class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class PartnerAppointment(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_RESPONDED = "responded"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_RESPONDED, "Responded"),
        (STATUS_CLOSED, "Closed"),
    ]

    organization_name = models.CharField(max_length=180)
    contact_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=60, blank=True)
    topic = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_response = models.TextField(blank=True)
    response_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.organization_name} ({self.contact_name})"
