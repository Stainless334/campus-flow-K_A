from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Ticket


def home(request):
    tickets = Ticket.objects.all().order_by("id")
    return render(request, "tickets/home.html", {"tickets": tickets})


def create_ticket(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        category = request.POST.get("category", "")
        urgency = request.POST.get("urgency", "")
        affected_users = request.POST.get("affected_users", "")

        if not title or not category or not urgency or not affected_users:
            return HttpResponse("Please fill in all fields.", status=400)

        try:
            affected_users = int(affected_users)
            if affected_users < 0:
                return HttpResponse(
                    "Affected users cannot be negative.", status=400
                )
        except ValueError:
            return HttpResponse("Enter a valid number of affected users.", status=400)

        if category not in dict(Ticket.CATEGORY_CHOICES):
            return HttpResponse("Invalid category.", status=400)

        if urgency not in dict(Ticket.URGENCY_CHOICES):
            return HttpResponse("Invalid urgency.", status=400)

        # Calculate priority using the CampusFlow rules.
        if urgency == "high" and affected_users >= 10:
            priority = "critical"
        elif urgency == "high" or affected_users >= 10:
            priority = "high"
        elif urgency == "medium" or affected_users >= 3:
            priority = "medium"
        else:
            priority = "low"

        # Generate the next ticket ID, such as T001 or T002.
        existing_ids = Ticket.objects.values_list("id", flat=True)
        numbers = [
            int(ticket_id[1:])
            for ticket_id in existing_ids
            if ticket_id.startswith("T") and ticket_id[1:].isdigit()
        ]
        next_number = max(numbers, default=0) + 1
        ticket_id = f"T{next_number:03d}"

        Ticket.objects.create(
            id=ticket_id,
            title=title,
            category=category,
            urgency=urgency,
            affected_users=affected_users,
            priority=priority,
            status="open",
        )

        return redirect("home")

    return render(request, "tickets/create_ticket.html")
