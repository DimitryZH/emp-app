resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "employee_photo_bucket" {
  name          = "employee-photo-bucket-${random_id.bucket_suffix.hex}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.employee_photo_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}