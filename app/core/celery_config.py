timezone = "Asia/Ho_Chi_Minh"
enable_utc = True

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

task_default_queue = "default"
task_routes = {
    "app.tasks.data_statistics.*": {"queue": "default"},
    "app.tasks.job_scan.*": {"queue": "default"},
}

task_retry_max = 3
task_retry_delay = 5  # seconds

task_track_started = True
task_send_sent_event = True
task_send_task_received_event = True
