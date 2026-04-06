from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cda', methods=['POST'])
def cda():
    return render_template('cda.html')


@app.route('/result', methods=['POST'])
def result():
    # בדיקה בסיסית שהקובץ קיים בבקשה
    if 'chat_file' not in request.files:
        return "לא נבחר קובץ", 400

    file = request.files['chat_file']

    # בדיקה שהמשתמש באמת בחר קובץ (שם הקובץ אינו ריק)
    if file.filename == '':
        return "שם קובץ ריק", 400

    if file:
        # שמירת הקובץ בתיקייה שהגדרנו מראש
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # --- שלב הניתוח ---

        user_counts = {}  # יצירת מילון ריק לאחסון שמות המשתמשים וכמות ההודעות שלהם

        # פתיחת הקובץ ששמרנו לקריאה בלבד ('r') עם תמיכה בעברית (utf-8)
        with open(file_path, 'r', encoding='utf-8') as f:
            # מעבר בלולאה על כל שורה ושורה בתוך הקובץ
            for line in f:
                # בוואטסאפ הודעה תקנית מכילה " - " בין התאריך לשם, ונקודתיים ":" אחרי השם
                if " - " in line and ":" in line:
                    try:
                        # 1. חיתוך השורה לפי המקף ולקיחת החלק שאחריו (החלק עם השם והטקסט)
                        after_date = line.split(" - ", 1)[1]

                        # 2. חיתוך לפי הנקודתיים הראשונות כדי לבודד רק את שם המשתמש
                        sender = after_date.split(":", 1)[0]

                        # 3. עדכון הספירה במילון: אם השם קיים נוסיף 1, אם לא - נגדיר כ-1
                        user_counts[sender] = user_counts.get(sender, 0) + 1
                    except IndexError:
                        # במקרה של שורה בפורמט לא מוכר (כמו הודעת מערכת), נמשיך הלאה
                        continue

        # בדיקה אם הצלחנו למצוא משתמשים בכלל
        if not user_counts:
            return "לא נמצאו נתונים לניתוח בקובץ שהועלה."

        # מציאת המשתמש עם מספר ההודעות הגבוה ביותר במילון
        top_user = max(user_counts, key=user_counts.get)
        max_messages = user_counts[top_user]

        # שליחת הנתונים לדף התוצאות (או החזרת טקסט פשוט לבדיקה)
        #return f"ניתוח הושלם! המשתמש הכי פעיל הוא <b>{top_user}</b> עם <b>{max_messages}</b> הודעות."

        if file and user_counts:
            top_user = max(user_counts, key=user_counts.get)
            max_messages = user_counts[top_user]

            # שליחת המשתנים לדף ה-HTML
            return render_template('end.html', winner_name=top_user, count=max_messages)

        return "לא נמצאו נתונים", 400

























if __name__ == '__main__':
    app.run(host= '0.0.0.0',port = 3000, debug=True)