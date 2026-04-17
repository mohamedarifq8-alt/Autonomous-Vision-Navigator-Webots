from controller import Robot
import cv2
import numpy as np

# ==========================================
# 1. التهيئة الأساسية للروبوت والمحركات
# ==========================================
robot = Robot()
time_step = int(robot.getBasicTimeStep())
MAX_SPEED = 6.28 # أقصى سرعة لمحركات e-puck

left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# ==========================================
# 2. تهيئة الكاميرا والحساسات
# ==========================================
camera = robot.getDevice('camera')
camera.enable(time_step)
width = camera.getWidth()
height = camera.getHeight()

ps = []
for i in range(8):
    sensor = robot.getDevice(f'ps{i}')
    sensor.enable(time_step)
    ps.append(sensor)

print("--------------------------------------------------")
print("النظام جاهز: الروبوت سيبدأ الآن باستكشاف المتاهة بذكاء...")
print("--------------------------------------------------")

# ==========================================
# 3. حلقة العمل الرئيسية (عقل الروبوت)
# ==========================================
while robot.step(time_step) != -1:
    
    # ----------------------------------------------------
    # أ. الذكاء الاصطناعي (استخراج اللون وتنظيف الصورة)
    # ----------------------------------------------------
    raw_img = camera.getImage()
    if not raw_img:
        continue
        
    # تحويل الصورة إلى مصفوفة تناسب حسابات OpenCV
    img = np.frombuffer(raw_img, np.uint8).reshape((height, width, 4))[:, :, :3]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # تحديد درجات اللون الأحمر
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    
    # دمج النطاقين لإنشاء القناع المبدئي
    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    
    # --- الفلترة المورفولوجية (تنظيف التشويش) ---
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)  # تآكل لحذف النقط الصغيرة المتناثرة
    mask = cv2.dilate(mask, kernel, iterations=1) # تمدد لاستعادة حجم الكرة الأساسي
    
    # البحث عن الأشكال داخل القناع النظيف
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    ball_detected = False
    cx = 0
    area = 0
    
    if contours:
        # اختيار أكبر شكل لتأكيد أنه الهدف
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # الحد الأدنى للمساحة هو 50 لزيادة الأمان ضد أي تشويش متبقٍ
        if area >40: 
            M = cv2.moments(largest_contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00']) 
                ball_detected = True

    # ----------------------------------------------------
    # ب. نوافذ المراقبة الهندسية (Debug Windows)
    # ----------------------------------------------------
    # تكبير الصور 4 مرات لكي تراها بوضوح
    enlarged_img = cv2.resize(img, (width * 4, height * 4), interpolation=cv2.INTER_NEAREST)
    enlarged_mask = cv2.resize(mask, (width * 4, height * 4), interpolation=cv2.INTER_NEAREST)
    
    cv2.imshow("Raw Camera Feed (Colored)", enlarged_img)
    cv2.imshow("AI Vision - Cleaned Mask", enlarged_mask)
    cv2.waitKey(1) 

    # ----------------------------------------------------
    # ج. دمج القرار (العتاد + الذكاء الاصطناعي)
    # ----------------------------------------------------
    # قراءة حساسات المسافة
    ps_values = [ps[i].getValue() for i in range(8)]
    
    # السرعة الافتراضية
    left_speed = MAX_SPEED * 0.7
    right_speed = MAX_SPEED * 0.7

    if ball_detected:
        # === 1. حالة رصد الكرة ===
        print(f"الهدف مرصود! يتم التوجيه نحو الكرة... الحجم: {area}")
        
        # حساب الخطأ عن المركز لتوجيه الروبوت بسلاسة
        error = (width / 2) - cx
        left_speed = MAX_SPEED * 0.5 - (error * 0.05)
        right_speed = MAX_SPEED * 0.5 + (error * 0.05)
        
        # شرط التوقف (تأكد من تعديل الرقم 160 إذا لزم الأمر)
        if area >3000: 
            left_motor.setVelocity(0.0)
            right_motor.setVelocity(0.0)
            print("==================================================")
            print("المهمة اكتملت: الروبوت أمام الكرة مباشرة!")
            print("==================================================")
            break 
            
    else:
        # === 2. خوارزمية تتبع الجدار الأيمن للبحث عن الكرة ===
        front_wall = ps_values[0] > 120 or ps_values[7] > 120
        right_wall = ps_values[1] > 80 or ps_values[2] > 80
        
        if front_wall:
            # حالة الطوارئ: جدار أمامي -> انعطف لليسار بقوة
            left_speed = -MAX_SPEED * 0.5
            right_speed = MAX_SPEED * 0.5
        else:
            if right_wall:
                # الجدار على اليمين -> امشِ بجانبه ووازن المسافة
                if ps_values[2] > 150: 
                    # قريب جداً من الجدار -> ابتعد قليلاً (لليسار)
                    left_speed = MAX_SPEED * 0.5
                    right_speed = MAX_SPEED * 0.7 
                elif ps_values[2] < 90: 
                    # تبتعد عن الجدار -> اقترب قليلاً (لليمين)
                    left_speed = MAX_SPEED * 0.7
                    right_speed = MAX_SPEED * 0.5 
            else:
                # فقدنا الجدار الأيمن -> انعطف في قوس واسع لليمين للبحث عنه
                left_speed = MAX_SPEED * 0.6
                right_speed = MAX_SPEED * 0.2

    # ----------------------------------------------------
    # د. إرسال الأوامر للمحركات
    # ----------------------------------------------------
    # حماية المحركات من تجاوز الحد الأقصى للسرعة
    left_speed = max(min(left_speed, MAX_SPEED), -MAX_SPEED)
    right_speed = max(min(right_speed, MAX_SPEED), -MAX_SPEED)
    
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)