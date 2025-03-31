from django.db import models

class Video(models.Model):
    video_id = models.AutoField(primary_key=True)
    video_url = models.URLField(max_length=2000, null=False)
    csv_path = models.TextField(null=True)

    def __str__(self):
        return f"Video {self.video_id}: {self.url}: {self.csv_path}"
