from django.db import models
from datetime import datetime
from time import timezone
from unittest import result
from venv import create
from django.conf import Settings
from django.db import DatabaseError, models
from django.core.validators import MaxValueValidator, MinValueValidator
# import re, uuid, jsonfield
from accounts.models import user
from django.forms import IntegerField
# from django.contrib.