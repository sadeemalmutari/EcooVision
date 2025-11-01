from django.db import models
from django.conf import settings
import os
from django.utils import timezone

def define_image_path(instance, filename):
    return os.path.join('faces', f'{instance.pk}.jpg')

def delete_file(file_field):
    if file_field and os.path.isfile(file_field.path):
        os.remove(file_field.path)

class Room(models.Model):
    name = models.CharField(max_length=100)
    light_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=100)
    about = models.TextField(blank=True)
    face_encoding = models.TextField(blank=True)
    image = models.ImageField(upload_to=define_image_path, blank=True, null=True, default='person_placeholder.jpg')
    enter_date = models.TimeField(blank=True, null=True)
    exit_date = models.TimeField(blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, related_name='owner')
    in_house = models.BooleanField(default=True)
    def is_in_house(self):
        return self.room is not None

    def save(self, *args, **kwargs):
        try:
            old_image = Person.objects.get(pk=self.pk).image
            if old_image and old_image != self.image and old_image.name != 'person_placeholder.jpg':
                delete_file(old_image)
        except Person.DoesNotExist:
            pass
        super(Person, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image.name != 'person_placeholder.jpg':
            delete_file(self.image)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

class Activity(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    enter_date = models.TimeField(blank=True, null=True)
    exit_date = models.TimeField(blank=True, null=True)
    action = models.CharField(max_length=100 , blank=True)
    actual_enter_date = models.DateTimeField(blank=True, null=True)
    actual_exit_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='activities', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.room:
            self.room.light_status = True if self.enter_date else False
            self.room.save()

        update_house_status()

        if self.pk:
            try:
                old_image = Activity.objects.get(pk=self.pk).image
                if old_image and old_image != self.image:
                    delete_file(old_image)
            except Activity.DoesNotExist:
                pass

        super(Activity, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            delete_file(self.image)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.person.name} activity in {self.room.name if self.room else 'N/A'}"

def update_house_status():
    is_house_empty = not Person.objects.filter(room__isnull=False).exists()
    if is_house_empty:
        Room.objects.update(light_status=False)