from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class BodyAnalysis(models.Model):
    class ActivityLevel(models.TextChoices):
        SEDENTARY = 'SEDENTARY', _('น้อย (นั่งทำงานเป็นหลัก/ไม่ออกกำลังกาย)')
        LIGHTLY_ACTIVE = 'LIGHTLY', _('ปานกลาง (ออกกำลังกาย 1-3 วัน/สัปดาห์)')
        MODERATELY_ACTIVE = 'MODERATE', _('ปานกลางค่อนข้างหนัก (ออกกำลังกาย 3-5 วัน/สัปดาห์)')
        VERY_ACTIVE = 'VERY', _('หนัก (ออกกำลังกาย 6-7 วัน/สัปดาห์)')
        EXTRA_ACTIVE = 'EXTRA', _('หนักมาก (นักกีฬา/ทำงานใช้แรงงาน)')

    class Gender(models.TextChoices):
        MALE = 'M', _('ชาย')
        FEMALE = 'F', _('หญิง')

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้ใช้งาน")
    
    # ข้อมูลทั่วไป
    age = models.PositiveIntegerField(verbose_name="อายุ (ปี)")
    weight = models.FloatField(verbose_name="น้ำหนัก (กก.)")
    height = models.FloatField(verbose_name="ส่วนสูง (ซม.)")
    gender = models.CharField(
        max_length=1, 
        choices=Gender.choices, 
        default=Gender.FEMALE, 
        verbose_name="เพศ"
    )
    activity_level = models.CharField(
        max_length=10, 
        choices=ActivityLevel.choices, 
        default=ActivityLevel.SEDENTARY, 
        verbose_name="ระดับกิจกรรม"
    )

    # สัดส่วนร่างกาย
    bust = models.FloatField(verbose_name="รอบอก (ซม.)")
    waist = models.FloatField(verbose_name="รอบเอว (ซม.)")
    hip = models.FloatField(verbose_name="รอบสะโพก (ซม.)")

    # Result Fields
    bmi = models.FloatField(null=True, blank=True, verbose_name="ค่า BMI")
    bmi_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="เกณฑ์ BMI")
    whr = models.FloatField(null=True, blank=True, verbose_name="WHR (Waist-to-Hip Ratio)")
    body_shape = models.CharField(max_length=50, null=True, blank=True, verbose_name="รูปร่าง")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ทำรายการ")

    class Meta:
        verbose_name = "ผลการวิเคราะห์รูปร่าง"
        verbose_name_plural = "ผลการวิเคราะห์รูปร่าง"
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def calculate_stats(self):
        # 1. Calculate BMI
        height_m = self.height / 100
        self.bmi = round(self.weight / (height_m ** 2), 2)
        
        if self.bmi < 18.5:
            self.bmi_status = "น้ำหนักต่ำกว่าเกณฑ์"
        elif 18.5 <= self.bmi <= 22.9:
            self.bmi_status = "สมส่วน"
        elif 23.0 <= self.bmi <= 24.9:
            self.bmi_status = "น้ำหนักเกิน"
        elif 25.0 <= self.bmi <= 29.9:
            self.bmi_status = "อ้วนระดับ 1"
        else:
            self.bmi_status = "อ้วนระดับ 2"

        # 2. Calculate WHR
        if self.hip > 0:
            self.whr = round(self.waist / self.hip, 2)
        else:
            self.whr = 0

        # 3. Determine Body Shape
        ratio = self.whr
        shape = "ไม่ระบุ"
        
        # Helper to check bust/hip balance for overlapping ranges
        bust_hip_ratio = self.bust / self.hip if self.hip > 0 else 1.0

        if ratio >= 0.85:
            shape = "หุ่นแอปเปิ้ล"
        elif 0.78 <= ratio < 0.85:
            # Overlap: Rectangle (0.78-0.82) vs Inverted Triangle (0.78-0.85)
            # Inverted Triangle usually has broader bust/shoulders
            if bust_hip_ratio > 1.05: 
                shape = "หุ่นสามเหลี่ยมบน"
            elif ratio <= 0.82:
                shape = "หุ่นทรงกระบอก"
            else:
                shape = "หุ่นสามเหลี่ยมบน"
        elif 0.68 <= ratio < 0.78:
            # Overlap: Hourglass (0.68-0.75) vs Pear (0.70-0.78)
            # Pear has Hip > Bust significantly
            if bust_hip_ratio < 0.95:
                shape = "หุ่นสามเหลี่ยมล่าง"
            elif ratio <= 0.75:
                shape = "หุ่นนาฬิกาทราย"
            else:
                 shape = "หุ่นสามเหลี่ยมล่าง"
        else:
            # Fallback for out of range
            if ratio < 0.68:
                shape = "หุ่นนาฬิกาทราย"
            else:
                shape = "หุ่นทรงกระบอก"
        
        self.body_shape = shape
        self.save()

    def get_image_folder(self):
        """Returns the folder name for the body shape images"""
        if not self.body_shape:
            return ""
        return self.body_shape.replace("หุ่น", "")

    def get_workout_schedule(self):
        # Returns list of dicts: { 'exercise': str, 'sets': str, 'reps': str, 'image': str }
        workouts = {
            "หุ่นนาฬิกาทราย": [
                {'exercise': 'Squat', 'sets': '3', 'reps': '10-12', 'image': 'Squat.gif'},
                {'exercise': 'Hip Thrust', 'sets': '3', 'reps': '10-12', 'image': 'Hip Thrust.gif'},
                {'exercise': 'Push-up', 'sets': '3', 'reps': '8-12', 'image': 'Push-up.gif'},
                {'exercise': 'Plank', 'sets': '3', 'reps': '30-45 วินาที', 'image': 'Plank.gif'},
                {'exercise': 'เดินเร็ว', 'sets': '-', 'reps': '15-20 นาที', 'image': 'Walk.gif'},
            ],
            "หุ่นสามเหลี่ยมล่าง": [
                {'exercise': 'Shoulder Press', 'sets': '4', 'reps': '10-12', 'image': 'Shoulder Press.gif'},
                {'exercise': 'Lateral Raise', 'sets': '3', 'reps': '12-15', 'image': 'Lateral Raise.gif'},
                {'exercise': 'Glute Bridge', 'sets': '3', 'reps': '12-15', 'image': 'Glute Bridge.gif'},
                {'exercise': 'Step-up', 'sets': '3', 'reps': '10/ข้าง', 'image': 'Step-up.gif'},
                {'exercise': 'เดินชัน', 'sets': '-', 'reps': '20 นาที', 'image': 'เดินชัน.gif'},
            ],
            "หุ่นทรงกระบอก": [
                {'exercise': 'Hip Thrust', 'sets': '4', 'reps': '8-12', 'image': 'Hip Thrust.gif'},
                {'exercise': 'Romanian Deadlift', 'sets': '3', 'reps': '8-12', 'image': 'Romanian Dead.gif'},
                {'exercise': 'Lateral Raise', 'sets': '3', 'reps': '12-15', 'image': 'Lateral Raise.gif'},
                {'exercise': 'Russian Twist', 'sets': '3', 'reps': '12-16', 'image': 'Russian Twist.gif'},
                {'exercise': 'Walk', 'sets': '-', 'reps': '15-20 นาที', 'image': 'Walk.gif'},
            ],
            "หุ่นสามเหลี่ยมบน": [
                {'exercise': 'Squat', 'sets': '4', 'reps': '8-12', 'image': 'squat.gif'},
                {'exercise': 'Hip Thrust', 'sets': '4', 'reps': '10-12', 'image': 'Hip Thrust.gif'},
                {'exercise': 'Bulgarian Split Squat', 'sets': '3', 'reps': '8/ข้าง', 'image': 'Bulgarian Split Squat.gif'},
                {'exercise': 'Side Plank', 'sets': '3', 'reps': '25-40 วินาที', 'image': 'Side Plank.gif'},
                {'exercise': 'เดินชันเบา', 'sets': '-', 'reps': '15 นาที', 'image': 'เดินชัน.gif'},
            ],
            "หุ่นแอปเปิ้ล": [
                {'exercise': 'Walk', 'sets': '-', 'reps': '20-30 นาที', 'image': 'Walk.gif'},
                {'exercise': 'Lat Pulldown', 'sets': '3', 'reps': '12-15', 'image': 'Lat Pulldown.gif'},
                {'exercise': 'Dead Bug', 'sets': '3', 'reps': '10-12', 'image': 'Dead Bug.gif'},
                {'exercise': 'Plank (เข่า)', 'sets': '3', 'reps': '20-30 วินาที', 'image': 'Knee Plank .JPG'},
                {'exercise': 'Glute Bridge', 'sets': '3', 'reps': '12-15', 'image': 'Glute Bridge.gif'},
            ],
        }
        return workouts.get(self.body_shape, [])
