"""
Trilingual Dictionary (v6 — expanded)
Maps terms across English, Arabic, and Kurdish Sorani.

v6 additions:
- 40 Business, Accounting & Finance term groups
- 38 Medical & Healthcare term groups
Total: ~294 groups, ~1200+ terms
"""

from typing import List, Dict, Set


class TermGroup:
    def __init__(self, en: List[str], ar: List[str], ckb: List[str], category: str = ""):
        self.en = [t.lower() for t in en]
        self.ar = ar
        self.ckb = ckb
        self.category = category
        self.all_terms = set(self.en + self.ar + self.ckb)


DICTIONARY: List[TermGroup] = []

def _add(en, ar, ckb, cat=""):
    DICTIONARY.append(TermGroup(en, ar, ckb, cat))


# ---- PROGRAMMING LANGUAGES ----
_add(["python"], ["بايثون", "بايثن"], ["پایتۆن"], "programming")
_add(["javascript", "js"], ["جافاسكربت", "جافا سكريبت"], ["جاڤاسکریپت"], "programming")
_add(["java"], ["جافا"], ["جاڤا"], "programming")
_add(["c++", "cpp"], ["سي بلس بلس"], ["سی پلەس پلەس"], "programming")
_add(["c#", "csharp", "c sharp"], ["سي شارب"], ["سی شارپ"], "programming")
_add(["php"], ["بي اتش بي"], ["پی ئێچ پی"], "programming")
_add(["ruby"], ["روبي"], ["ڕووبی"], "programming")
_add(["swift"], ["سويفت"], ["سویفت"], "programming")
_add(["kotlin"], ["كوتلن"], ["کۆتلین"], "programming")
_add(["go", "golang"], ["غو", "جو"], ["گۆ"], "programming")
_add(["rust"], ["رست"], ["ڕەست"], "programming")
_add(["typescript", "ts"], ["تايب سكربت"], ["تایپسکریپت"], "programming")
_add(["r language", "r programming"], ["لغة ار"], ["زمانی ئار"], "programming")
_add(["dart"], ["دارت"], ["دارت"], "programming")
_add(["scala"], ["سكالا"], ["سکالا"], "programming")
_add(["perl"], ["بيرل"], ["پێرل"], "programming")
_add(["sql"], ["اس كيو ال"], ["ئێس کیو ئێل"], "programming")
_add(["bash", "shell script"], ["باش", "شل"], ["باش"], "programming")
_add(["programming", "coding", "programming language"], ["برمجة", "لغة برمجة"], ["پرۆگرامکردن", "زمانی پرۆگرامکردن", "کۆدکردن"], "programming")

# ---- WEB TECHNOLOGIES ----
_add(["html", "html5"], ["اتش تي ام ال"], ["ئێچ تی ئێم ئێل"], "web")
_add(["css", "css3"], ["سي اس اس"], ["سی ئێس ئێس"], "web")
_add(["react", "reactjs", "react.js"], ["رياكت"], ["ڕیئاکت"], "web")
_add(["angular", "angularjs"], ["انجولار"], ["ئانگولار"], "web")
_add(["vue", "vuejs", "vue.js"], ["فيو"], ["ڤیو"], "web")
_add(["node", "nodejs", "node.js"], ["نود"], ["نۆد"], "web")
_add(["express", "expressjs"], ["اكسبرس"], ["ئێکسپرێس"], "web")
_add(["django"], ["جانغو"], ["جانگۆ"], "web")
_add(["flask"], ["فلاسك"], ["فلاسک"], "web")
_add(["fastapi", "fast api"], ["فاست اي بي اي"], ["فاست ئەی پی ئای"], "web")
_add(["spring", "spring boot"], ["سبرنج"], ["سپرینگ"], "web")
_add(["laravel"], ["لارافل"], ["لاراڤێل"], "web")
_add(["asp.net", "asp", "dotnet", ".net"], ["دوت نت"], ["دۆت نێت"], "web")
_add(["next.js", "nextjs"], ["نكست"], ["نێکست"], "web")
_add(["bootstrap"], ["بوتستراب"], ["بووتستراپ"], "web")
_add(["tailwind", "tailwind css"], ["تيلويند"], ["تەیلوایند"], "web")
_add(["jquery"], ["جيكويري"], ["جێکوێری"], "web")
_add(["rest", "rest api", "restful"], ["رست اي بي اي", "واجهة برمجية"], ["ڕێست ئەی پی ئای"], "web")
_add(["graphql"], ["جراف كيو ال"], ["گراف کیو ئێل"], "web")
_add(["json"], ["جيسون"], ["جەیسۆن"], "web")
_add(["xml"], ["اكس ام ال"], ["ئێکس ئێم ئێل"], "web")
_add(["api"], ["واجهة برمجية", "اي بي اي"], ["ئەی پی ئای"], "web")
_add(["web development", "web developer"], ["تطوير الويب", "تطوير مواقع", "مطور ويب"], ["گەشەپێدانی وێب", "گەشەپێدەری وێب"], "web")
_add(["frontend", "front end", "front-end"], ["واجهة أمامية", "فرونت اند"], ["ڕووکاری پێشەوە", "فرۆنت ئێند"], "web")
_add(["backend", "back end", "back-end"], ["خلفية", "باك اند"], ["لای سێرڤەر", "باک ئێند"], "web")
_add(["full stack", "fullstack", "full-stack"], ["فل ستاك", "مطور متكامل"], ["فوڵ ستاک", "تەواو پەشکۆ"], "web")
_add(["responsive design"], ["تصميم متجاوب"], ["دیزاینی ڕیسپۆنسیڤ"], "web")
_add(["wordpress"], ["ووردبريس"], ["وۆردپرێس"], "web")

# ---- DATABASES ----
_add(["database", "db"], ["قاعدة بيانات", "قاعدة البيانات"], ["بنکەی داتا", "داتابەیس"], "database")
_add(["mysql"], ["ماي اس كيو ال"], ["مای ئێس کیو ئێل"], "database")
_add(["postgresql", "postgres"], ["بوستجري"], ["پۆستگرێس"], "database")
_add(["mongodb", "mongo"], ["مونجو"], ["مۆنگۆ"], "database")
_add(["sqlite"], ["اس كيو لايت"], ["ئێس کیو لایت"], "database")
_add(["redis"], ["ريدس"], ["ڕێدیس"], "database")
_add(["oracle"], ["اوراكل"], ["ئۆراکڵ"], "database")
_add(["sql server", "mssql"], ["اس كيو ال سيرفر"], ["ئێس کیو ئێل سێرڤەر"], "database")
_add(["firebase"], ["فايربيس"], ["فایەربەیس"], "database")
_add(["nosql", "no sql"], ["نو اس كيو ال"], ["نۆ ئێس کیو ئێل"], "database")
_add(["elasticsearch"], ["الاستك سيرش"], ["ئیلاستیک سێرچ"], "database")

# ---- CLOUD & DEVOPS ----
_add(["docker"], ["دوكر"], ["دۆکەر"], "devops")
_add(["kubernetes", "k8s"], ["كوبرنيتس"], ["کوبەرنێتس"], "devops")
_add(["aws", "amazon web services"], ["أمازون ويب سيرفس"], ["ئەی دەبلیو ئێس"], "devops")
_add(["azure", "microsoft azure"], ["ازور"], ["ئەژوور"], "devops")
_add(["gcp", "google cloud"], ["جوجل كلاود"], ["گووگل کلاود"], "devops")
_add(["devops"], ["ديف اوبس"], ["دێڤئۆپس"], "devops")
_add(["ci/cd", "cicd", "continuous integration"], ["تكامل مستمر"], ["ئینتیگریشنی بەردەوام"], "devops")
_add(["jenkins"], ["جنكنز"], ["جێنکینز"], "devops")
_add(["terraform"], ["تيرافورم"], ["تێرافۆرم"], "devops")
_add(["ansible"], ["انسبل"], ["ئانسیبڵ"], "devops")
_add(["cloud computing"], ["الحوسبة السحابية", "كلاود"], ["هەورکۆمپیوتینگ", "کلاود"], "devops")
_add(["server"], ["خادم", "سيرفر"], ["سێرڤەر"], "devops")
_add(["linux"], ["لينكس"], ["لینوکس"], "devops")
_add(["windows"], ["ويندوز"], ["ویندۆز"], "devops")
_add(["nginx"], ["انجنكس"], ["ئێنجینکس"], "devops")
_add(["apache"], ["اباتشي"], ["ئاپاچی"], "devops")

# ---- SOFTWARE ENGINEERING CONCEPTS ----
_add(["algorithm", "algorithms"], ["خوارزمية", "خوارزميات"], ["ئالگۆریزم", "ئالگۆریزمەکان"], "engineering")
_add(["data structure", "data structures"], ["هيكلة بيانات", "بنية بيانات"], ["پێکهاتەی داتا"], "engineering")
_add(["software engineering"], ["هندسة البرمجيات", "هندسة برمجيات"], ["ئەندازیاری نەرمەکاڵا"], "engineering")
_add(["object oriented", "oop", "object-oriented programming"], ["برمجة كائنية"], ["ئۆبجێکت ئۆرینتید"], "engineering")
_add(["design pattern", "design patterns"], ["انماط التصميم"], ["پاتێرنی دیزاین"], "engineering")
_add(["testing", "software testing", "unit test"], ["اختبار", "اختبار البرمجيات"], ["تاقیکردنەوە", "تاقیکردنەوەی نەرمەکاڵا"], "engineering")
_add(["debugging", "debug"], ["تصحيح الأخطاء"], ["هەڵەدۆزینەوە", "دیباگکردن"], "engineering")
_add(["version control"], ["التحكم بالإصدارات"], ["کۆنتڕۆڵی وەشان"], "engineering")
_add(["git"], ["جت"], ["گیت"], "engineering")
_add(["github"], ["جت هب"], ["گیتهەب"], "engineering")
_add(["agile"], ["اجايل", "أجايل"], ["ئاجایل"], "engineering")
_add(["scrum"], ["سكرم"], ["سکرەم"], "engineering")
_add(["jira"], ["جيرا"], ["جیرا"], "engineering")
_add(["framework"], ["إطار عمل", "فريم ورك"], ["چوارچێوە", "فرەیموۆرک"], "engineering")
_add(["library"], ["مكتبة"], ["کتێبخانە"], "engineering")
_add(["clean code"], ["كود نظيف"], ["کۆدی پاک"], "engineering")
_add(["documentation", "docs"], ["توثيق", "وثائق"], ["بەڵگەنامەکردن"], "engineering")
_add(["code review"], ["مراجعة الكود"], ["پێداچوونەوەی کۆد"], "engineering")
_add(["software development"], ["تطوير البرمجيات"], ["گەشەپێدانی نەرمەکاڵا"], "engineering")
_add(["architecture", "software architecture"], ["هندسة معمارية", "بنية البرمجيات"], ["ئارکیتێکچەر", "بنیاتی نەرمەکاڵا"], "engineering")
_add(["microservices"], ["خدمات مصغرة"], ["مایکرۆسێرڤیس"], "engineering")
_add(["performance", "optimization"], ["أداء", "تحسين"], ["ئەدا", "باشترکردن"], "engineering")

# ---- MOBILE DEVELOPMENT ----
_add(["mobile development", "mobile app"], ["تطوير تطبيقات الموبايل", "تطبيقات الهاتف"], ["گەشەپێدانی مۆبایل", "ئەپی مۆبایل"], "mobile")
_add(["android"], ["اندرويد"], ["ئاندرۆید"], "mobile")
_add(["ios"], ["اي او اس"], ["ئای ئۆ ئێس"], "mobile")
_add(["react native"], ["رياكت نيتف"], ["ڕیئاکت نەیتیڤ"], "mobile")
_add(["flutter"], ["فلتر"], ["فلەتەر"], "mobile")

# ---- DATA & AI ----
_add(["machine learning", "ml"], ["تعلم الآلة", "تعلم آلي"], ["فێربوونی مەکینە"], "data")
_add(["artificial intelligence", "ai"], ["الذكاء الاصطناعي", "ذكاء اصطناعي"], ["زیرەکی دەستکرد"], "data")
_add(["deep learning"], ["التعلم العميق"], ["فێربوونی قووڵ"], "data")
_add(["data science"], ["علم البيانات"], ["زانستی داتا"], "data")
_add(["data analysis", "data analyst"], ["تحليل البيانات", "محلل بيانات"], ["شیکاری داتا"], "data")
_add(["big data"], ["البيانات الضخمة"], ["داتای گەورە"], "data")
_add(["tensorflow"], ["تنسرفلو"], ["تێنسۆرفلۆ"], "data")
_add(["pytorch"], ["باي تورش"], ["پای تۆرچ"], "data")
_add(["natural language processing", "nlp"], ["معالجة اللغة الطبيعية"], ["پرۆسێسکردنی زمانی سروشتی"], "data")
_add(["computer vision"], ["رؤية حاسوبية"], ["بینایی کۆمپیوتەر"], "data")
_add(["neural network"], ["شبكة عصبية"], ["تۆڕی دەماری"], "data")
_add(["data mining"], ["تنقيب البيانات"], ["کانکردنی داتا"], "data")
_add(["statistics", "statistical analysis"], ["إحصاء", "تحليل إحصائي"], ["ئامار", "شیکاری ئاماری"], "data")
_add(["pandas"], ["بانداز"], ["پانداز"], "data")
_add(["numpy"], ["نمباي"], ["نەمپای"], "data")
_add(["power bi"], ["باور بي اي"], ["پاوەر بی ئای"], "data")
_add(["tableau"], ["تابلو"], ["تابلۆ"], "data")
_add(["excel", "microsoft excel"], ["اكسل"], ["ئێکسێل"], "data")

# ---- NETWORKING & SECURITY ----
_add(["network", "networking"], ["شبكة", "شبكات"], ["تۆڕ", "تۆڕکاری"], "network")
_add(["security", "cybersecurity", "information security"], ["أمن", "أمن المعلومات", "أمن سيبراني"], ["ئاسایش", "ئاسایشی زانیاری", "سایبەرسکیوریتی"], "network")
_add(["firewall"], ["جدار ناري"], ["فایەروۆڵ"], "network")
_add(["encryption"], ["تشفير"], ["شفرەکردن"], "network")
_add(["vpn"], ["في بي ان"], ["ڤی پی ئێن"], "network")
_add(["tcp/ip", "tcp ip"], ["تي سي بي"], ["تی سی پی"], "network")
_add(["operating system", "os"], ["نظام تشغيل"], ["سیستەمی کارپێکردن"], "network")

# ---- DESIGN ----
_add(["design", "graphic design"], ["تصميم", "تصميم جرافيك"], ["دیزاین", "دیزاینی گرافیک"], "design")
_add(["ui", "user interface"], ["واجهة المستخدم"], ["ڕووکاری بەکارهێنەر"], "design")
_add(["ux", "user experience"], ["تجربة المستخدم"], ["ئەزموونی بەکارهێنەر"], "design")
_add(["ui/ux", "ui ux"], ["واجهة وتجربة المستخدم"], ["یو ئای / یو ئێکس"], "design")
_add(["figma"], ["فيجما"], ["فیگما"], "design")
_add(["photoshop", "adobe photoshop"], ["فوتوشوب"], ["فۆتۆشۆپ"], "design")
_add(["illustrator", "adobe illustrator"], ["اليستريتور"], ["ئیلەستریتۆر"], "design")
_add(["adobe xd"], ["ادوبي اكس دي"], ["ئادۆبی ئێکس دی"], "design")
_add(["sketch"], ["سكتش"], ["سکێچ"], "design")
_add(["wireframe", "prototype"], ["نموذج أولي", "واير فريم"], ["وایەرفرەیم", "پرۆتۆتایپ"], "design")
_add(["indesign"], ["انديزاين"], ["ئیندیزاین"], "design")

# ---- JOB TITLES & ROLES ----
_add(["software engineer", "software developer"], ["مهندس برمجيات", "مطور برمجيات"], ["ئەندازیاری نەرمەکاڵا", "گەشەپێدەری نەرمەکاڵا"], "role")
_add(["web developer"], ["مطور ويب"], ["گەشەپێدەری وێب"], "role")
_add(["mobile developer"], ["مطور تطبيقات"], ["گەشەپێدەری مۆبایل"], "role")
_add(["data engineer"], ["مهندس بيانات"], ["ئەندازیاری داتا"], "role")
_add(["data scientist"], ["عالم بيانات"], ["زانای داتا"], "role")
_add(["system administrator", "sysadmin"], ["مدير نظام"], ["بەڕێوەبەری سیستەم"], "role")
_add(["network engineer"], ["مهندس شبكات"], ["ئەندازیاری تۆڕ"], "role")
_add(["project manager", "pm"], ["مدير مشروع", "مدير المشاريع"], ["بەڕێوەبەری پرۆژە"], "role")
_add(["team leader", "team lead", "tech lead"], ["قائد فريق", "رئيس فريق"], ["سەرۆکی تیم", "لیدەری تیم"], "role")
_add(["developer", "programmer", "coder"], ["مطور", "مبرمج"], ["گەشەپێدەر", "پرۆگرامەر", "کۆدەر"], "role")
_add(["devops engineer"], ["مهندس ديف اوبس"], ["ئەندازیاری دێڤئۆپس"], "role")
_add(["qa engineer", "quality assurance", "tester"], ["مهندس ضمان الجودة", "مختبر"], ["ئەندازیاری کوالیتی", "تاقیکەرەوە"], "role")
_add(["analyst", "business analyst"], ["محلل", "محلل أعمال"], ["شیکار", "شیکاری بزنس"], "role")
_add(["designer", "graphic designer"], ["مصمم", "مصمم جرافيك"], ["دیزاینەر", "دیزاینەری گرافیک"], "role")
_add(["manager", "director"], ["مدير"], ["بەڕێوەبەر", "مودیر"], "role")
_add(["intern", "trainee", "internship"], ["متدرب", "تدريب"], ["ئینتێرن", "ڕاهێنان"], "role")
_add(["freelancer", "freelance"], ["عمل حر", "فريلانسر"], ["فریلانسەر", "سەربەخۆ"], "role")
_add(["consultant"], ["مستشار"], ["ڕاوێژکار"], "role")
_add(["technical support", "it support"], ["دعم فني", "دعم تقني"], ["پشتگیری تەکنیکی"], "role")
_add(["instructor", "trainer", "teacher"], ["مدرب", "معلم"], ["مامۆستا", "ڕاهێنەر", "فێرکار"], "role")

# ---- EDUCATION & DEGREES ----
_add(["bachelor", "bsc", "b.sc", "bachelor's", "bachelors degree"], ["بكالوريوس"], ["بەکالۆریۆس"], "education")
_add(["master", "msc", "m.sc", "master's", "masters degree"], ["ماجستير"], ["ماستەر"], "education")
_add(["phd", "doctorate", "ph.d"], ["دكتوراه", "دكتوراة"], ["دکتۆرا", "پی ئێچ دی"], "education")
_add(["diploma"], ["دبلوم"], ["دیبلۆم"], "education")
_add(["certificate", "certification"], ["شهادة"], ["بڕوانامە", "سەرتیفیکەیت"], "education")
_add(["high school"], ["ثانوية", "شهادة ثانوية"], ["ئامادەیی"], "education")
_add(["computer science", "cs"], ["علوم الحاسوب", "علوم حاسب"], ["زانستی کۆمپیوتەر"], "education")
_add(["information technology", "it"], ["تقنية المعلومات", "تكنولوجيا المعلومات"], ["تەکنەلۆجیای زانیاری"], "education")
_add(["software engineering"], ["هندسة البرمجيات"], ["ئەندازیاری نەرمەکاڵا"], "education")
_add(["university"], ["جامعة", "الجامعة"], ["زانکۆ"], "education")
_add(["college"], ["كلية"], ["کۆلێج"], "education")
_add(["education"], ["تعليم", "التعليم"], ["خوێندن", "پەروەردە"], "education")
_add(["gpa", "grade point average"], ["معدل تراكمي"], ["نمرەی گشتی", "جی پی ئەی"], "education")
_add(["graduate", "graduation"], ["تخرج", "خريج"], ["دەرچوون", "دەرچوو"], "education")

# ---- SOFT SKILLS ----
_add(["communication", "communication skills"], ["تواصل", "مهارات التواصل"], ["پەیوەندیکردن", "لێهاتوویی پەیوەندیکردن"], "soft")
_add(["teamwork", "team work"], ["عمل جماعي", "عمل فريقي"], ["کاری تیمی", "کارکردن وەک تیم"], "soft")
_add(["leadership"], ["قيادة", "مهارات القيادة"], ["سەرکردایەتی", "لیدەرشیپ"], "soft")
_add(["problem solving"], ["حل المشكلات", "حل مشاكل"], ["چارەسەرکردنی کێشە"], "soft")
_add(["critical thinking"], ["تفكير نقدي", "التفكير النقدي"], ["بیرکردنەوەی ڕەخنەیی"], "soft")
_add(["time management"], ["إدارة الوقت"], ["بەڕێوەبردنی کات"], "soft")
_add(["creativity", "creative"], ["إبداع", "ابداعي"], ["داهێنان", "داهێنانە"], "soft")
_add(["adaptability", "flexible"], ["مرونة", "تكيف"], ["گونجان", "نەرم"], "soft")
_add(["attention to detail"], ["الاهتمام بالتفاصيل"], ["سەرنجدان بە وردەکاری"], "soft")
_add(["analytical", "analytical skills"], ["تحليلي", "مهارات تحليلية"], ["شیکارکاری", "لێهاتوویی شیکاری"], "soft")
_add(["presentation", "presentation skills"], ["عرض", "مهارات العرض"], ["پێشکەشکردن", "لێهاتوویی پێشکەشکردن"], "soft")
_add(["motivation", "self motivated"], ["تحفيز", "ذاتي التحفيز"], ["پاڵنەر", "خۆپاڵنەر"], "soft")
_add(["organization", "organizational"], ["تنظيم", "تنظيمي"], ["ڕێکخستن", "ڕێکخراوی"], "soft")
_add(["planning"], ["تخطيط"], ["پلاندانان"], "soft")
_add(["decision making"], ["اتخاذ القرار", "صنع القرار"], ["بڕیاردان"], "soft")
_add(["negotiation"], ["تفاوض"], ["دانوستان"], "soft")
_add(["multitasking"], ["تعدد المهام"], ["چەند کاری لە یەک کاتدا"], "soft")

# ---- BUSINESS & MANAGEMENT (original) ----
_add(["project management"], ["إدارة المشاريع", "ادارة مشاريع"], ["بەڕێوەبردنی پرۆژە"], "business")
_add(["management"], ["إدارة", "ادارة"], ["بەڕێوەبردن"], "business")
_add(["marketing", "digital marketing"], ["تسويق", "تسويق رقمي"], ["مارکێتینگ", "بازاڕکردنی دیجیتاڵ"], "business")
_add(["sales"], ["مبيعات"], ["فرۆشتن"], "business")
_add(["customer service"], ["خدمة العملاء", "خدمة عملاء"], ["خزمەتگوزاری کڕیار"], "business")
_add(["business development"], ["تطوير الأعمال"], ["گەشەپێدانی بزنس"], "business")
_add(["strategy", "strategic"], ["استراتيجية", "استراتيجي"], ["ستراتیجی"], "business")
_add(["budget", "budgeting"], ["ميزانية"], ["بودجە"], "business")
_add(["accounting"], ["محاسبة"], ["ژمێریاری"], "business")
_add(["finance", "financial"], ["مالية", "مالي"], ["دارایی"], "business")
_add(["human resources", "hr"], ["موارد بشرية"], ["سەرچاوەی مرۆیی", "ئێچ ئار"], "business")

# ---- COMMON HR / WORK VOCABULARY ----
_add(["experience", "work experience"], ["خبرة", "خبرة عملية"], ["ئەزموون", "ئەزموونی کار"], "hr")
_add(["skills", "skill"], ["مهارات", "مهارة"], ["لێهاتوویی", "تواناکان"], "hr")
_add(["resume", "cv", "curriculum vitae"], ["سيرة ذاتية"], ["سی ڤی", "ناساندنی خۆ"], "hr")
_add(["job", "position"], ["وظيفة", "منصب"], ["کار", "پۆست"], "hr")
_add(["salary", "compensation"], ["راتب", "تعويض"], ["موچە", "مووچە"], "hr")
_add(["interview"], ["مقابلة"], ["چاوپێکەوتن"], "hr")
_add(["company", "organization"], ["شركة", "مؤسسة"], ["کۆمپانیا", "دامەزراوە"], "hr")
_add(["work", "working"], ["عمل"], ["کار", "کارکردن"], "hr")
_add(["requirement", "requirements"], ["متطلبات", "متطلب"], ["پێویستی", "پێداویستیەکان"], "hr")
_add(["responsibility", "responsibilities"], ["مسؤولية", "مسؤوليات"], ["بەرپرسیاریەتی", "ئەرکەکان"], "hr")
_add(["training"], ["تدريب"], ["ڕاهێنان"], "hr")
_add(["professional"], ["احترافي", "مهني"], ["پیشەیی", "پرۆفیشناڵ"], "hr")
_add(["year", "years"], ["سنة", "سنوات"], ["ساڵ", "ساڵان"], "hr")
_add(["knowledge"], ["معرفة"], ["زانیاری", "زانین"], "hr")
_add(["ability", "capable"], ["قدرة", "قادر"], ["توانا", "لێهاتوو"], "hr")
_add(["volunteer", "volunteering"], ["تطوع"], ["خۆبەخش", "خۆبەخشانە"], "hr")
_add(["reference", "references"], ["مرجع", "مراجع"], ["سەرچاوە", "ڕیفرێنس"], "hr")

# ==============================================================
# NEW IN v6: BUSINESS, ACCOUNTING & FINANCE (40 groups)
# ==============================================================
_add(["auditing", "audit"], ["تدقيق", "مراجعة حسابات"], ["ئۆدیتکردن", "پشکنین"], "accounting")
_add(["bookkeeping"], ["مسك الدفاتر"], ["تۆمارکردنی حساب"], "accounting")
_add(["financial statement", "financial statements"], ["قوائم مالية", "بيان مالي"], ["ڕاپۆرتی دارایی"], "accounting")
_add(["balance sheet"], ["ميزانية عمومية"], ["هاوسەنگی دارایی", "بیلانس شیت"], "accounting")
_add(["income statement", "profit and loss"], ["قائمة الدخل", "بيان الأرباح والخسائر"], ["ڕاپۆرتی داهات"], "accounting")
_add(["tax", "taxation"], ["ضريبة", "ضرائب"], ["باج", "باجدان"], "accounting")
_add(["payroll"], ["رواتب", "كشف الرواتب"], ["موچەدان", "لیستی موچە"], "accounting")
_add(["invoice", "invoicing"], ["فاتورة", "فوترة"], ["وەسڵ", "فاتوورە"], "accounting")
_add(["accounts payable"], ["ذمم دائنة"], ["حسابی بێدەر"], "accounting")
_add(["accounts receivable"], ["ذمم مدينة"], ["حسابی وەرگر"], "accounting")
_add(["general ledger"], ["دفتر الأستاذ"], ["دەفتەری سەرەکی"], "accounting")
_add(["cost accounting"], ["محاسبة التكاليف"], ["ژمێریاری تێچوون"], "accounting")
_add(["financial analysis"], ["تحليل مالي"], ["شیکاری دارایی"], "accounting")
_add(["cash flow"], ["تدفق نقدي"], ["گەردوونی پارە", "کاش فلۆ"], "accounting")
_add(["revenue"], ["إيرادات", "عائدات"], ["داهات"], "accounting")
_add(["expense", "expenses", "expenditure"], ["مصروفات", "نفقات"], ["خەرجی", "تێچوون"], "accounting")
_add(["profit", "profitability"], ["ربح", "أرباح"], ["قازانج"], "accounting")
_add(["loss"], ["خسارة", "خسائر"], ["زەرەر"], "accounting")
_add(["investment", "investing"], ["استثمار"], ["وەبەرهێنان"], "accounting")
_add(["banking", "bank"], ["مصرفي", "بنك"], ["بانک", "بانکداری"], "accounting")
_add(["loan", "lending"], ["قرض", "إقراض"], ["قەرز", "قەرزدان"], "accounting")
_add(["interest rate"], ["سعر الفائدة"], ["ڕێژەی قازانج"], "accounting")
_add(["insurance"], ["تأمين"], ["بیمە"], "accounting")
_add(["stock", "stocks", "shares", "equity"], ["أسهم", "حصص"], ["سهام", "پشک"], "accounting")
_add(["bond", "bonds"], ["سندات"], ["بۆند"], "accounting")
_add(["asset", "assets"], ["أصول", "موجودات"], ["سامان", "دارایی"], "accounting")
_add(["liability", "liabilities"], ["التزامات", "خصوم"], ["قەرزایەتی"], "accounting")
_add(["depreciation"], ["استهلاك", "إهلاك"], ["خاوکردنەوە"], "accounting")
_add(["economics", "economy"], ["اقتصاد", "اقتصادي"], ["ئابووری"], "accounting")
_add(["supply chain", "supply chain management"], ["سلسلة التوريد", "إدارة سلسلة التوريد"], ["زنجیرەی دابینکردن"], "accounting")
_add(["procurement", "purchasing"], ["مشتريات", "شراء"], ["کڕین", "دابینکردن"], "accounting")
_add(["inventory", "stock management"], ["مخزون", "إدارة المخزون"], ["کۆگا", "بەڕێوەبردنی کۆگا"], "accounting")
_add(["accountant"], ["محاسب"], ["ژمێریار"], "accounting")
_add(["financial advisor"], ["مستشار مالي"], ["ڕاوێژکاری دارایی"], "accounting")
_add(["treasurer"], ["أمين الصندوق"], ["خەزنەدار"], "accounting")
_add(["erp", "enterprise resource planning"], ["تخطيط موارد المؤسسة"], ["ئی ئار پی"], "accounting")
_add(["quickbooks"], ["كويك بوكس"], ["کویکبووکس"], "accounting")
_add(["sap"], ["ساب", "اس اي بي"], ["ساپ"], "accounting")
_add(["trade", "trading", "import export"], ["تجارة", "استيراد وتصدير"], ["بازرگانی", "هاوردە و ناردە"], "accounting")
_add(["contract", "contracts"], ["عقد", "عقود"], ["گرێبەست", "پەیمان"], "accounting")

# ==============================================================
# NEW IN v6: MEDICAL & HEALTHCARE (38 groups)
# ==============================================================
_add(["medicine", "medical"], ["طب", "طبي"], ["پزیشکی"], "medical")
_add(["doctor", "physician"], ["طبيب", "دكتور"], ["پزیشک", "دکتۆر"], "medical")
_add(["nurse", "nursing"], ["ممرض", "تمريض"], ["پەرستار", "پەرستاری"], "medical")
_add(["pharmacist", "pharmacy"], ["صيدلي", "صيدلة"], ["دەرمانساز", "دەرمانسازی"], "medical")
_add(["surgeon", "surgery"], ["جراح", "جراحة"], ["نەشتەرگەر", "نەشتەرگەری"], "medical")
_add(["dentist", "dental", "dentistry"], ["طبيب أسنان", "طب أسنان"], ["پزیشکی ددان", "ددانپزیشک"], "medical")
_add(["hospital"], ["مستشفى"], ["نەخۆشخانە", "خەستەخانە"], "medical")
_add(["clinic"], ["عيادة", "مستوصف"], ["کلینیک", "پزیشکخانە"], "medical")
_add(["patient", "patients"], ["مريض", "مرضى"], ["نەخۆش", "نەخۆشەکان"], "medical")
_add(["diagnosis", "diagnostic"], ["تشخيص"], ["دەستنیشانکردنی نەخۆشی"], "medical")
_add(["treatment", "therapy"], ["علاج", "معالجة"], ["چارەسەر", "دەرمانکردن"], "medical")
_add(["prescription"], ["وصفة طبية"], ["ڕەچەتە"], "medical")
_add(["laboratory", "lab", "medical lab"], ["مختبر", "مختبر طبي"], ["تاقیگە", "لابەراتوار"], "medical")
_add(["radiology", "x-ray", "imaging"], ["أشعة", "تصوير"], ["تیشکدانەوە", "وێنەگرتن"], "medical")
_add(["ultrasound"], ["تصوير بالأمواج فوق الصوتية"], ["ئەلتراساوند", "سۆنار"], "medical")
_add(["mri", "magnetic resonance"], ["تصوير بالرنين المغناطيسي"], ["ئێم ئار ئای"], "medical")
_add(["blood test", "blood work"], ["تحليل دم", "فحص دم"], ["پشکنینی خوێن"], "medical")
_add(["vaccine", "vaccination", "immunization"], ["لقاح", "تطعيم"], ["ڤاکسین", "دەرزی بەرگری"], "medical")
_add(["anesthesia", "anesthesiology"], ["تخدير"], ["بێهۆشکردن", "بنج"], "medical")
_add(["cardiology", "cardiologist"], ["أمراض القلب", "طب القلب"], ["نەخۆشیەکانی دڵ"], "medical")
_add(["neurology", "neurologist"], ["أمراض الأعصاب", "طب الأعصاب"], ["نەخۆشیەکانی دەمار"], "medical")
_add(["pediatrics", "pediatrician"], ["طب الأطفال"], ["پزیشکی منداڵان"], "medical")
_add(["dermatology", "dermatologist"], ["أمراض جلدية", "طب الجلد"], ["پزیشکی پێست"], "medical")
_add(["ophthalmology", "eye doctor"], ["طب العيون"], ["پزیشکی چاو"], "medical")
_add(["orthopedics"], ["جراحة العظام"], ["ئێسکبەندی"], "medical")
_add(["emergency", "emergency medicine", "er"], ["طوارئ", "طب الطوارئ"], ["فریاکەوتن", "قەوارە"], "medical")
_add(["intensive care", "icu"], ["عناية مركزة"], ["چاودێری سەخت"], "medical")
_add(["physical therapy", "physiotherapy"], ["علاج طبيعي"], ["فیزیۆتراپی", "چارەسەری سروشتی"], "medical")
_add(["mental health", "psychiatry"], ["صحة نفسية", "طب نفسي"], ["تەندروستی دەروونی"], "medical")
_add(["medical record", "health record", "ehr"], ["سجل طبي", "سجل صحي"], ["تۆماری پزیشکی"], "medical")
_add(["health", "healthcare"], ["صحة", "رعاية صحية"], ["تەندروستی", "چاودێری تەندروستی"], "medical")
_add(["clinical", "clinical trial"], ["سريري", "تجربة سريرية"], ["کلینیکی", "تاقیکردنەوەی کلینیکی"], "medical")
_add(["anatomy"], ["تشريح"], ["جەستەناسی"], "medical")
_add(["pathology"], ["علم الأمراض"], ["زانستی نەخۆشی"], "medical")
_add(["epidemiology"], ["علم الأوبئة"], ["زانستی بڵاوبوونەوەی نەخۆشی"], "medical")
_add(["public health"], ["صحة عامة"], ["تەندروستی گشتی"], "medical")
_add(["medical equipment", "medical devices"], ["أجهزة طبية", "معدات طبية"], ["ئامێری پزیشکی"], "medical")
_add(["first aid"], ["إسعافات أولية"], ["یارمەتی یەکەم"], "medical")


# ==============================================================
# LOOKUP STRUCTURES — built once at import time
# ==============================================================

_TERM_TO_GROUPS: Dict[str, List[int]] = {}

for idx, group in enumerate(DICTIONARY):
    for term in group.all_terms:
        lower = term.lower()
        if lower not in _TERM_TO_GROUPS:
            _TERM_TO_GROUPS[lower] = []
        _TERM_TO_GROUPS[lower].append(idx)


def get_all_groups() -> List[TermGroup]:
    return DICTIONARY

def get_group_count() -> int:
    return len(DICTIONARY)

def find_groups_for_term(term: str) -> List[TermGroup]:
    indices = _TERM_TO_GROUPS.get(term.lower(), [])
    return [DICTIONARY[i] for i in indices]

def get_all_terms_flat() -> Set[str]:
    return set(_TERM_TO_GROUPS.keys())

def get_category_groups(category: str) -> List[TermGroup]:
    return [g for g in DICTIONARY if g.category == category]
