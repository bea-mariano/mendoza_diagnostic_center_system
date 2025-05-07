import qrcode

# Replace this with your static content
data = "http://54.252.161.188/patient/new/"

img = qrcode.make(data)

# Save the QR image
img.save("new_patient.png")
