from django.db import migrations


def seed_content(apps, schema_editor):
    Program = apps.get_model("applications", "Program")
    Project = apps.get_model("applications", "Project")
    Event = apps.get_model("applications", "Event")
    TeamMember = apps.get_model("applications", "TeamMember")
    Testimonial = apps.get_model("applications", "Testimonial")

    if Program.objects.exists() or Project.objects.exists() or Event.objects.exists() or TeamMember.objects.exists() or Testimonial.objects.exists():
        return

    programs = [
        {
            "title": "Early Learning Foundations",
            "focus": "School readiness",
            "description": "Play-based learning, literacy, and numeracy support for young learners.",
            "status": "Active",
            "beneficiaries": "Children ages 3+",
            "highlights": [
                "Foundational literacy and numeracy activities",
                "Safe and inclusive early childhood spaces",
                "Parent engagement for home learning",
            ],
        },
        {
            "title": "Education Retention and Policy",
            "focus": "Access and equity",
            "description": "Community advocacy and school retention support for vulnerable children.",
            "status": "Active",
            "beneficiaries": "Learners at risk of dropping out",
            "highlights": [
                "Back-to-school campaigns and follow-up",
                "Case support for at-risk learners",
                "Community policy dialogue on education access",
            ],
        },
        {
            "title": "Arts and Crafts Livelihoods",
            "focus": "Women-led enterprise",
            "description": "Skills training in crochet, beadwork, and design for income generation.",
            "status": "Open enrollment",
            "beneficiaries": "Women-led households",
            "highlights": [
                "Practical craft and design training",
                "Market linkage and small business coaching",
                "Income pathways for women-led households",
            ],
        },
    ]

    for i, item in enumerate(programs, start=1):
        Program.objects.create(display_order=i, is_active=True, **item)

    projects = [
        {
            "title": "Community Learning Labs",
            "tag": "Education",
            "copy": "After-school tutoring, digital literacy, and mentorship in safe learning spaces.",
        },
        {
            "title": "Safe Homes Network",
            "tag": "Protection",
            "copy": "Case support, family referrals, and child safeguarding follow-up.",
        },
        {
            "title": "Women in Enterprise",
            "tag": "Livelihoods",
            "copy": "Business skills, savings circles, and market linkage support for caregivers.",
        },
    ]

    for i, item in enumerate(projects, start=1):
        Project.objects.create(display_order=i, is_active=True, **item)

    events = [
        {
            "title": "Back-to-School Learning Fair",
            "date": "2026-03-20",
            "location": "Kakuma Learning Hub",
            "tag": "Education",
            "description": "Enrollment support, school kits, and parent orientation.",
            "highlights": [
                "School enrollment and re-enrollment desk",
                "Learning kits and caregiver orientation",
                "Child-friendly activity stations",
            ],
        },
        {
            "title": "Women in Artistry Showcase",
            "date": "2026-04-12",
            "location": "Community Market Hall",
            "tag": "Livelihoods",
            "description": "Community exhibition of crochet, beadwork, and design.",
            "highlights": [
                "Live demonstrations and product displays",
                "Sales and market exposure for women groups",
                "Networking with potential partners",
            ],
        },
        {
            "title": "Family Unity Dialogue",
            "date": "2026-05-08",
            "location": "EUTR Community Center",
            "tag": "Community",
            "description": "Public forum on child protection and social cohesion.",
            "highlights": [
                "Community dialogue on safeguarding",
                "Referral pathways for vulnerable children",
                "Joint commitments for social cohesion",
            ],
        },
    ]

    for i, item in enumerate(events, start=1):
        Event.objects.create(display_order=i, is_active=True, **item)

    team = [
        {
            "name": "M.A. Malony",
            "role": "Founder and Executive Director",
            "copy": "Leads the vision for early learning, equity, and community care.",
        },
        {
            "name": "Maggiso L.",
            "role": "Programs Coordinator",
            "copy": "Coordinates learning circles and family engagement.",
        },
        {
            "name": "Linet Achieng",
            "role": "Education Lead",
            "copy": "Strengthens foundational learning and teacher support.",
        },
        {
            "name": "Joseph Wanjala",
            "role": "Community Partnerships",
            "copy": "Builds partnerships with schools and local leaders.",
        },
        {
            "name": "Rose Atieno",
            "role": "Women in Enterprise",
            "copy": "Guides arts and crafts training for women-led households.",
        },
        {
            "name": "Peter Lomo",
            "role": "Protection Officer",
            "copy": "Leads child protection, safeguarding, and referrals.",
        },
        {
            "name": "Grace Njeri",
            "role": "Monitoring and Learning",
            "copy": "Tracks impact and shares evidence for better programs.",
        },
    ]

    for i, item in enumerate(team, start=1):
        TeamMember.objects.create(display_order=i, is_active=True, **item)

    testimonials = [
        {
            "name": "M.A. Malony",
            "role": "Founder, EUTR",
            "quote": "Our mission is practical: start early, protect learning, and ensure every child in Kakuma is ready to thrive.",
        },
        {
            "name": "Linet Achieng",
            "role": "Education Lead",
            "quote": "When children receive foundational support, their confidence grows, attendance improves, and families stay hopeful.",
        },
        {
            "name": "Community Parent Leader",
            "role": "Parent Representative",
            "quote": "EUTR gives our children structure and joy. The vision is visible in every classroom and every parent meeting.",
        },
    ]

    for i, item in enumerate(testimonials, start=1):
        Testimonial.objects.create(display_order=i, is_active=True, **item)


def unseed_content(apps, schema_editor):
    Program = apps.get_model("applications", "Program")
    Project = apps.get_model("applications", "Project")
    Event = apps.get_model("applications", "Event")
    TeamMember = apps.get_model("applications", "TeamMember")
    Testimonial = apps.get_model("applications", "Testimonial")

    Program.objects.all().delete()
    Project.objects.all().delete()
    Event.objects.all().delete()
    TeamMember.objects.all().delete()
    Testimonial.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0002_contactmessage_event_program_project_teammember_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
