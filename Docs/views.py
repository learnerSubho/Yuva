from django.shortcuts import render
from django.templatetags.static import static
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def dash(request):
    return render(request,'home.html')
@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def gene(request):
    if request.method == "POST":
        # Fetch details from the form
        name = request.POST.get('name', 'default')
        guardian = request.POST.get('guardian', 'default')
        course = request.POST.get('course', 'default')
        aclass = request.POST.get('aclass', 'default')
        session = request.POST.get('session', 'default')
        duration = request.POST.get('duration', 'default')
        grade = request.POST.get('grade', 'default')
        currdate = date.today().strftime(r"%d/%m/%Y")
        uploaded_file = request.FILES.get('image')

        # Save the uploaded image temporarily
        if uploaded_file:
            image_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(image_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
        else:
            image_path = None

        # Locate the PDF template
        static_file_path = os.path.join(settings.STATICFILES_DIRS[0], 'TCKA.pdf')

        def certificate():
            # Create a folder for certificates if it doesn't exist
            if not os.path.exists('Certificates'):
                os.makedirs('Certificates')

            output_path = f'Certificates/Certificate.pdf'

            # Check if the base PDF template exists
            if not os.path.exists(static_file_path):
                print(f"Error: {static_file_path} not found.")
                return None

            # Read the template PDF
            reader = PdfReader(static_file_path)
            writer = PdfWriter()
            page = reader.pages[0]

            # Add text and image to the PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=landscape(A4))

            # Add text fields
            fields = [
                (460, 308, name),
                (275, 265, guardian),
                (185, 222, course),
                (514, 222, aclass),
                (218, 180, session),
                (460, 180, duration),
                (232, 138, grade),
                (578, 138, currdate),
                (170, 100, currdate),
            ]
            for x, y, text in fields:
                c.setFont("Times-BoldItalic", 18)
                c.drawString(x, y, text)

            # Add candidate image if uploaded
            if image_path and os.path.exists(image_path):
                c.drawImage(image_path, 640, 340, width=80, height=100)  # Adjust position and size

            c.save()
            buffer.seek(0)

            # Merge the overlay with the template
            overlay = PdfReader(buffer)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

            # Write the final output
            with open(output_path, 'wb') as f:
                writer.write(f)

            print(f"Certificate saved to {output_path}")
            return output_path

        # Generate the certificate
        output_path = certificate()

        # Clean up the temporary image file
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

        # Pass the certificate path to the view
        parameter = {
            'URL': output_path,
            'Name': name,
        }
        return render(request, 'view.html', parameter)