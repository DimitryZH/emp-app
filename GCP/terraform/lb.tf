resource "google_compute_global_address" "default" {
  name = "employee-web-app-ip"
}

resource "google_compute_backend_service" "default" {
  name        = "employee-web-app-backend"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10

  health_checks = [google_compute_health_check.autohealing.id]

  backend {
    group = google_compute_region_instance_group_manager.app_mig.instance_group
  }
}

resource "google_compute_url_map" "default" {
  name            = "employee-web-app-url-map"
  default_service = google_compute_backend_service.default.id
}

resource "google_compute_target_http_proxy" "default" {
  name    = "employee-web-app-http-proxy"
  url_map = google_compute_url_map.default.id
}

resource "google_compute_global_forwarding_rule" "default" {
  name       = "employee-web-app-forwarding-rule"
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.default.address
}

output "load_balancer_ip" {
  value = google_compute_global_address.default.address
}