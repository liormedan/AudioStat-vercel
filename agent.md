ליאור, הנה “תיאור סוכן” מדויק וקונקרטי שתוכל להדביק בעורך קוד (או בכל Agent Builder) כדי שיבנה עבורך את הכלי בפרונטנד של Vercel.

# תיאור סוכן: Audio AutoSeat (Frontend on Vercel)

## תפקיד

את/ה סוכן/ית קוד שבונה אפליקציית ווב קלה שמזהה מתוך קובץ אודיו את **BPM**, מציעה **Tempo Map** בסיסי, מזהה **סולם (Key)**, ומייצאת **קובץ MIDI** עם מטא־אירועי טמפו/מרקר—הכול בקליינט, לפריסה ב־Vercel.

## יעדים

1. ניתוח אודיו בצד לקוח: BPM גלובלי, הערכת סולם (major/minor), בסיס למפת טמפו.
2. יצוא `tempo_map.mid` (Meta Tempo + Marker לטקסט Key).
3. UI מינימלי: העלאת קובץ, תצוגת תוצאות, כפתור הורדה ל־MIDI.
4. קוד Production-Ready: TypeScript, Next.js 15 (App Router), ללא תלות בשרת.

## אילוצים

* הכול רץ בדפדפן (אין שרת/FFmpeg/Essentia).
* ספריות מותרות: `meyda`, `musictempo`, `midi-writer-js`.
* אין שימוש בצבעים/סגנונות כבדים; Tailwind כתוספת אופציונלית.
* תמיכה ב־WAV/MP3; ניתוח ערוץ אחד (Mono downmix).

## ארכיטקטורה

* **Next.js 15 App Router**
* רכיב יחיד `AudioAutoSeat` שמטפל בהעלאה, דה־קוד, ניתוח, ויצוא MIDI.
* Utility קטן לזיהוי סולם בשיטת Krumhansl (פרופילי כרומה).

## פלטפורמה/התקנה

* יצירת פרויקט חדש: `pnpm dlx create-next-app@latest`
* ספריות:

  ```bash
  pnpm add meyda musictempo midi-writer-js
  # אופציונלי לעיצוב:
  pnpm add -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
* התאמות ל־TS וחוקי build של Vercel (ברירת מחדל מספיקה).

## מבנה ריפו מוצע

```
/ (root)
├─ app/
│  ├─ page.tsx
│  └─ components/
│     └─ AudioAutoSeat.tsx
├─ public/
├─ package.json
├─ tsconfig.json
└─ README.md
```

## משימות הסוכן (שלבים)

1. יצירת פרויקט Next.js 15 (App Router) והפעלת TypeScript.
2. התקנת `meyda`, `musictempo`, `midi-writer-js`.
3. כתיבת רכיב `AudioAutoSeat.tsx`:

   * קבלת קובץ `<input type="file" accept="audio/*">`
   * שימוש ב־`AudioContext.decodeAudioData` → Buffer → ערוץ אחד.
   * **BPM**: שימוש ב־`MusicTempo` על אנרגיית מסגרת (RMS/Onset proxy).
   * **Key**: חישוב כרומה ממוצעת עם `meyda.extract('chroma')` + התאמה ל־Krumhansl (major/minor).
   * **Tempo Map**: גרסה בסיסית – טמפו גלובלי, עם הערה בקוד היכן לשדרג לפיצ’ינג של סגמנטים.
   * **MIDI**: יצירת track עם `midi-writer-js`, `setTempo`, הוספת Meta Text `Key: X`. הפקה ל־Blob + URL להורדה.
   * UI: אזור גרירה/העלאה, מצב “מנתח…”, הצגת BPM/Key, כפתור “הורד MIDI”.
4. עמוד `app/page.tsx` שמרנדר את הרכיב ומציג הוראות קצרות.
5. כתיבת README עם הוראות הפעלה, מגבלות, ושדרוגים עתידיים.
6. בדיקות ידניות עם קבצי WAV/MP3 לדגימה.
7. הכנת הפרויקט לפריסה ב־Vercel (ברירת מחדל מספיקה, אין env).

## קבצים למימוש (תמצית)

* `app/components/AudioAutoSeat.tsx`

  * ניתוח אודיו (Meyda כרומה + RMS)
  * BPM: `new MusicTempo(energyArray)`
  * Key: פרופילים Major/Minor, התאמת כרומה ממוצעת
  * MIDI: `midi-writer-js` – `setTempo`, Meta Text “Key: …”
  * הורדת Blob כ־`.mid`
* `app/page.tsx` – מעטפת ו־UI.
* `README.md` – שימוש, מגבלות, מדריך לייבוא ב־Cubase:

  * **File → Import → MIDI File → Import Tempo Track**
  * גרירת האודיו ל־1|1|1|0
  * Musical Mode On/Off לפי צורך.

## קבלה (Acceptance Criteria)

* מעלים קובץ אודיו → מתקבלות תוצאות תוך ≤10 שניות לקובץ של 3–4 דקות במחשב ממוצע.
* מוצג BPM (מספר שלם מעוגל + ערך מדויק בתיעוד).
* מוצג Key (לדוגמה: `G major`).
* לחיצה על “הורד MIDI” יוצרת קובץ `tempo_map.mid`.
* ייבוא ה־MIDI ל־Cubase עם “Import Tempo Track” מסנכרן את סרגל הטמפו לפרויקט.
* קוד עובר build ב־Vercel ללא שגיאות.

## שדרוגים עתידיים (לסימון בקוד כ־TODO)

* חלון Advanced:

  * זיהוי downbeat מדויק יותר (onset strength + autocorr).
  * חלוקת Segments לטמפו משתנה (variance over beat intervals).
  * Markers לפי Key changes (כרומה בחלונות מתגלגלים).
* כפתור Export CSV ל־Markers (time,label).
* תמיכה בתצוגת גל/כרומה בסיסית (Canvas).

## הודעות שגיאה/מצבים

* אין WebAudio: להציג הודעה “הדפדפן לא תומך ב־AudioContext”.
* קובץ פגום/לא נתמך: “לא ניתן היה לפענח את האודיו”.
* תוצאות חלשות: להציג הודעת “איכות הניתוח מוגבלת—נסה קובץ WAV”.

## טקסטים ל־UI

* כותרת: “Audio AutoSeat – ניתוח BPM/Key וייצוא MIDI”
* כפתורי פעולה: “בחר קובץ”, “מנתח…”, “הורד MIDI”
* שדות תוצאה: “BPM”, “Key”, “Sample Rate (קריאה בלבד)”.

---

תרצה שאוסיף גם פקודות `pnpm` מלאות ו־README מוכן לקופי־פייסט, או אפילו שאארוז לך דוגמת ריפו מוכנה ל־Vercel?
