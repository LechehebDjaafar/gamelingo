<div dir="rtl" align="right">

# GameLingo — تعريب أي لعبة إلى أي لغة بمهارات Claude Code

[English](README.md)

**GameLingo** مجموعة مهارات لـ Claude Code تحلّل ملفات لعبة مثبّتة عندك (Steam أو Epic Games أو GOG أو مجلد يدوي)، تستخرج نصوصها، تترجمها مع مراعاة السياق والمصطلحات، تصلح عرض اللغات من اليمين إلى اليسار (العربية، الفارسية، الأردية، العبرية)، ثم تبني رقعة **قابلة للتراجع**.

## المزايا
- اكتشاف الألعاب المثبّتة تلقائيًا ومحرّكها (Unity، Unreal، Godot، RPG Maker، Ren'Py، GameMaker، Electron).
- ترجمة إلى **أي لغة** مع قاموس مصطلحات ثابت وحماية للمتغيرات مثل `{0}` و`%s` و`\C[2]`.
- معالجة العربية: وصل الحروف، ترتيب الاتجاه، والخطوط المناسبة.
- فحص جودة آلي وقائمة اختبار داخل اللعبة.
- نسخ احتياطي مُتحقَّق منه واسترجاع بأمر واحد، وبدون تعديل مباشر على ملفات اللعبة.

## التثبيت
```text
/plugin marketplace add YOUR_USERNAME/gamelingo
/plugin install gamelingo@gamelingo
```
أو شغّل `./install.sh` (ويندوز: `.\install.ps1`). للعربية: `python -m pip install -r requirements-rtl.txt`

## الاستخدام
في Claude Code اكتب مثلًا:
```text
ترجم اللعبة الموجودة في D:\SteamLibrary\steamapps\common\MyGame إلى العربية
```
أو استخدم الأوامر: `/gamelingo` و`/gamelingo-scan` و`/gamelingo-extract` و`/gamelingo-translate` و`/gamelingo-rtl` و`/gamelingo-qa` و`/gamelingo-pack` و`/gamelingo-restore`.

## ملاحظات مهمة
- ليست كل الألعاب مدعومة. راجع جدول الدعم في [README](README.md#engine-support) (الحالات: Stable / Beta / Experimental).
- استخدمها للألعاب الفردية التي تملكها فقط. تعديل ملفات ألعاب لها حماية ضد الغش قد يؤدي إلى حظر الحساب.
- شارك **ملفات الترجمة فقط** وليس ملفات اللعبة. راجع [الملاحظات القانونية](skills/gamelingo/references/legal-and-safety.md).
- بعد تحديث اللعبة أو "التحقق من الملفات" ستُمسح الرقعة، أعد تطبيقها.

## المساهمة
نرحب بوصفات المحركات ومعالجات الصيغ وخبرة العربية. اقرأ [CONTRIBUTING.md](CONTRIBUTING.md).

## الرخصة
MIT

</div>
