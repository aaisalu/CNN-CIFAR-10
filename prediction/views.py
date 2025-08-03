import json
import logging
import os
import uuid
from datetime import timedelta
from io import BytesIO

from .models import Prediction
from .utils import get_image_from_request, process_and_save_prediction
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


logger = logging.getLogger(__name__)


@login_required(login_url="/account/login")
def addpredict(request):
    target_dir = os.path.join(settings.MEDIA_ROOT, "images")
    os.makedirs(target_dir, exist_ok=True)

    if request.method != "POST":
        return render(request, "predictionform/form.html", {"error": ""})

    user_data = {
        "username": request.user.username,
        "user_id": request.user.id,
        "unique_filename": f"{request.user.username}_{request.user.id}_{uuid.uuid4().hex[:6]}",
    }

    img, error = get_image_from_request(request, user_data, target_dir)
    if error:
        messages.error(request, error)
        return render(request, "predictionform/form.html", {"error": error})

    try:
        prediction, error = process_and_save_prediction(img, request.user)
        if error:
            messages.error(request, error)
            return render(request, "predictionform/form.html", {"error": error})
        messages.success(request, "Your prediction has been submitted successfully.")
        return render(
            request, "predictionform/success.html", {"prediction": prediction}
        )
    except Exception as e:
        logger.error(f"Error processing image for user {request.user.id}: {e}")
        messages.error(request, "An error occurred while processing the image.")
        return render(request, "predictionform/form.html", {"error": str(e)})


@login_required(login_url="/account/login")
def prediction_history(request):
    if request.user.is_authenticated:
        prediction = Prediction.objects.filter(submitted_by=request.user).order_by(
            "-uploaded_at"
        )
        context = {"prediction": prediction}
        return render(request, "predictionform/predictionhistory.html", context)
    messages.error(request, "You must login to your account first")
    return redirect("login")


@login_required(login_url="/account/login")
def delete_prediction(request, prediction_id):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if request.method == "POST":
        prediction = get_object_or_404(
            Prediction, id=prediction_id, submitted_by=request.user
        )
        if prediction.image_file:
            image_path = prediction.image_file.path
            if os.path.isfile(image_path):
                os.remove(image_path)
        prediction.delete()
        messages.success(request, "Prediction deleted successfully.")
        return redirect("prediction_history")

    return redirect("prediction_history")


@login_required(login_url="/account/login")
def export_pdf(request):  # noqa: C901, PLR0915
    """Generate and export the prediction history as a PDF with images."""
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    predictions = Prediction.objects.filter(submitted_by=request.user).order_by(
        "-uploaded_at"
    )
    if not predictions.exists():
        messages.info(request, "No predictions found.")
        return HttpResponse("No data available", content_type="text/plain")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, letter_height = letter

    def setup_pdf_canvas():
        pdf.setTitle("Prediction History")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(230, letter_height - 50, "Prediction History")

    def draw_table_headers(y_pos):
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20, y_pos, "S.N")
        pdf.drawString(95, y_pos, "Image")
        pdf.drawString(225, y_pos, "Class A")
        pdf.drawString(325, y_pos, "Probability A")
        pdf.drawString(425, y_pos, "Class B")
        pdf.drawString(525, y_pos, "Probability B")
        pdf.drawString(625, y_pos, "Class C")
        pdf.drawString(725, y_pos, "Probability C")

    def draw_prediction_row(index, prediction, y_pos):
        pdf.drawString(20, y_pos, str(index))
        if prediction.image_file:
            try:
                image_path = os.path.join(
                    settings.MEDIA_ROOT, str(prediction.image_file)
                )
                with Image.open(image_path) as img:
                    img.thumbnail((50, 50))
                    img_buffer = BytesIO()
                    img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)
                    pdf.drawImage(
                        ImageReader(img_buffer), 95, y_pos - 20, width=50, height=50
                    )
            except Exception as e:
                pdf.drawString(95, y_pos, "[Error: Img]")
                messages.warning(request, f"Error loading image: {e}")
        pdf.drawString(225, y_pos, prediction.class_1 or "")
        pdf.drawString(325, y_pos, f"{prediction.prob_1}%" if prediction.prob_1 else "")
        pdf.drawString(425, y_pos, prediction.class_2 or "")
        pdf.drawString(525, y_pos, f"{prediction.prob_2}%" if prediction.prob_2 else "")
        pdf.drawString(625, y_pos, prediction.class_3 or "")
        pdf.drawString(725, y_pos, f"{prediction.prob_3}%" if prediction.prob_3 else "")

    def create_pdf_response(buffer):
        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=prediction_history.pdf"
        buffer.close()
        return response

    setup_pdf_canvas()
    y_position = letter_height - 100
    draw_table_headers(y_position)
    pdf.setFont("Helvetica", 12)
    y_position -= 50

    for index, p in enumerate(predictions, start=1):
        if y_position < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = letter_height - 50
            draw_table_headers(y_position)
            y_position -= 50
        draw_prediction_row(index, p, y_position)
        y_position -= 60

    pdf.showPage()
    pdf.save()
    return create_pdf_response(buffer)


# @cache_page(60 * 2)
@login_required(login_url="/account/login")
@user_passes_test(lambda u: u.is_superuser, login_url="/account/login")
def admin_dashboard(request):  # noqa: PLR0914
    """Admin dashboard with overview of key metrics."""
    # Total users
    total_users = User.objects.count()

    # Total predictions
    total_predictions = Prediction.objects.count()

    # Average predictions per user
    total_active_users = (
        User.objects.filter(prediction__isnull=False).distinct().count()
    )
    avg_predictions_per_user = (
        round(total_predictions / total_active_users, 2)
        if total_active_users > 0
        else 0
    )

    # Most predicted class (based on class_1)
    most_predicted = (
        Prediction.objects.exclude(class_1__isnull=True)
        .values("class_1")
        .annotate(count=Count("class_1"))
        .order_by("-count")
        .first()
    )
    most_predicted_class = most_predicted["class_1"] if most_predicted else "N/A"

    # Recent predictions (last 5)
    recent_predictions = Prediction.objects.select_related("submitted_by").order_by(
        "-uploaded_at"
    )[:5]

    # Predictions over the last 7 days for the chart
    today = timezone.now()
    start_date = today - timedelta(days=7)
    prediction_counts_by_date = (
        Prediction.objects.filter(uploaded_at__gte=start_date)
        .annotate(date=TruncDate("uploaded_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )
    date_counts = {entry["date"]: entry["count"] for entry in prediction_counts_by_date}
    chart_labels = []
    chart_data = []
    for i in range(7, -1, -1):
        date = (today - timedelta(days=i)).date()
        chart_labels.append(date.strftime("%Y-%m-%d"))
        chart_data.append(date_counts.get(date, 0))

    # New Stats
    # Recent user registrations (last 7 days)
    recent_users = User.objects.filter(date_joined__gte=start_date).count()

    # Top active users (top 5 by prediction count)
    top_active_users = (
        User.objects.filter(prediction__isnull=False)
        .annotate(prediction_count=Count("prediction"))
        .order_by("-prediction_count")[:5]
    )

    context = {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "avg_predictions_per_user": avg_predictions_per_user,
        "most_predicted_class": most_predicted_class,
        "recent_predictions": recent_predictions,
        "has_predictions": total_predictions > 0,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "recent_users": recent_users,
        "top_active_users": top_active_users,
    }
    return render(request, "index/dashboard.html", context)
