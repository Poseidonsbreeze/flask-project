from datetime import datetime, timedelta
from app.extensions import db
from app.models import Scholarship


SCHOLARSHIPS = [
    {
        "title": "Fulbright Foreign Student Program",
        "provider": "Fulbright",
        "country": "United States",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to international students from 155+ countries. Requires strong academic record, English proficiency, and demonstrated leadership potential.",
        "description": "The Fulbright Foreign Student Program provides full funding for graduate study in the United States. Covers tuition, airfare, living stipend, and health insurance for the duration of the program.",
        "deadline_offset": 90,
        "application_link": "https://foreign.fulbrightonline.org/"
    },
    {
        "title": "Chevening Scholarships",
        "provider": "UK Government",
        "country": "United Kingdom",
        "degree_level": "Master's",
        "eligibility": "Open to applicants from Chevening-eligible countries. Must have at least 2 years of work experience and a strong academic background.",
        "description": "Chevening Scholarships are fully funded master's degree awards at any UK university. Includes full tuition, living expenses, airfare, and visa costs.",
        "deadline_offset": 60,
        "application_link": "https://www.chevening.org/"
    },
    {
        "title": "DAAD Scholarship for Development-Related Postgraduate Courses",
        "provider": "DAAD",
        "country": "Germany",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to graduates from developing countries with at least 2 years of professional experience. Must have a bachelor's degree in a relevant field.",
        "description": "DAAD scholarships fund postgraduate courses in Germany that are specifically relevant to developing countries. Includes monthly stipend, travel allowance, health insurance, and tuition.",
        "deadline_offset": 120,
        "application_link": "https://www.daad.de/en/study-and-research-in-germany/scholarships/"
    },
    {
        "title": "Erasmus Mundus Joint Master Degrees",
        "provider": "European Union",
        "country": "Multiple (Europe)",
        "degree_level": "Master's",
        "eligibility": "Open to students worldwide with a bachelor's degree. Strong academic record required. Some programs require work experience.",
        "description": "Erasmus Mundus offers fully funded scholarships for joint master's programs delivered by consortia of European universities. Includes tuition, travel, living allowance, and insurance.",
        "deadline_offset": 75,
        "application_link": "https://erasmus-plus.ec.europa.eu/opportunities-for-individuals"
    },
    {
        "title": "Australia Awards Scholarships",
        "provider": "Australian Government",
        "country": "Australia",
        "degree_level": "Bachelor's, Master's, PhD",
        "eligibility": "Open to citizens of participating developing countries. Must meet academic requirements and return to home country for 2 years after completion.",
        "description": "Australia Awards are prestigious international scholarships for study at Australian universities. Covers full tuition, return airfare, establishment allowance, living expenses, and health cover.",
        "deadline_offset": 100,
        "application_link": "https://www.dfat.gov.au/people-to-people/australia-awards"
    },
    {
        "title": "Joint Japan/World Bank Graduate Scholarship Program",
        "provider": "World Bank",
        "country": "Multiple",
        "degree_level": "Master's",
        "eligibility": "Open to developing country nationals with at least 3 years of development-related work experience. Must hold a bachelor's degree.",
        "description": "The JJ/WBGSP provides full scholarships for graduate studies in development-related fields at top universities worldwide. Covers tuition, living stipend, travel, and medical insurance.",
        "deadline_offset": 85,
        "application_link": "https://www.worldbank.org/en/programs/scholarships"
    },
    {
        "title": "Gates Cambridge Scholarship",
        "provider": "Bill & Melinda Gates Foundation",
        "country": "United Kingdom",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to applicants from any country outside the UK. Must demonstrate academic excellence, leadership potential, and a commitment to improving the lives of others.",
        "description": "Gates Cambridge Scholarships provide full funding for graduate study at the University of Cambridge. Covers tuition, living allowance, travel, and academic development funding.",
        "deadline_offset": 45,
        "application_link": "https://www.gatescambridge.org/"
    },
    {
        "title": "Rhodes Scholarship",
        "provider": "Rhodes Trust",
        "country": "United Kingdom",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to eligible country citizens aged 18-24. Must demonstrate exceptional intellect, character, leadership, and commitment to service.",
        "description": "The Rhodes Scholarship is one of the oldest and most prestigious international scholarship programs, offering full funding for study at the University of Oxford. All-inclusive.",
        "deadline_offset": 30,
        "application_link": "https://www.rhodeshouse.ox.ac.uk/"
    },
    {
        "title": "Knight-Hennessy Scholars Program",
        "provider": "Stanford University",
        "country": "United States",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to applicants from all countries with a bachelor's degree. Must demonstrate independence of thought, purposeful leadership, and civic mindset.",
        "description": "Knight-Hennessy Scholars provides full funding for graduate study at Stanford University. Covers tuition, living stipend, travel, and academic enrichment opportunities.",
        "deadline_offset": 50,
        "application_link": "https://knight-hennessy.stanford.edu/"
    },
    {
        "title": "MEXT Scholarship (Research Students)",
        "provider": "Japanese Government",
        "country": "Japan",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to graduates under 35 from countries with diplomatic relations with Japan. Must have strong academic record in a field offered by Japanese universities.",
        "description": "MEXT scholarships fund international students for graduate research at Japanese universities. Includes tuition exemption, monthly allowance, travel, and accommodation support.",
        "deadline_offset": 110,
        "application_link": "https://www.mext.go.jp/en/"
    },
    {
        "title": "Swiss Government Excellence Scholarships",
        "provider": "Swiss Government",
        "country": "Switzerland",
        "degree_level": "PhD, Postdoctoral",
        "eligibility": "Open to graduates from all countries with a master's degree. Must have a research proposal accepted by a Swiss university supervisor.",
        "description": "Swiss Government Excellence Scholarships support doctoral and postdoctoral research at Swiss universities. Includes monthly stipend, tuition exemption, health insurance, and airfare.",
        "deadline_offset": 70,
        "application_link": "https://www.sbfi.admin.ch/sbfi/en/home/education/internationale-bildung.html"
    },
    {
        "title": "Vanier Canada Graduate Scholarship",
        "provider": "Canadian Government",
        "country": "Canada",
        "degree_level": "PhD",
        "eligibility": "Open to Canadian and international PhD students with a first-class average in their previous studies. Must demonstrate research potential and leadership.",
        "description": "Vanier CGS provides $50,000 per year for 3 years to doctoral students at Canadian universities. Recognizes research excellence and leadership in the social sciences, humanities, natural sciences, and health.",
        "deadline_offset": 55,
        "application_link": "https://vanier.gc.ca/"
    },
    {
        "title": "AAUW International Fellowships",
        "provider": "AAUW",
        "country": "United States",
        "degree_level": "Master's, PhD, Postdoctoral",
        "eligibility": "Open to women who are not US citizens or permanent residents. Must have a bachelor's degree and intend to return home to pursue a career.",
        "description": "AAUW International Fellowships support women from around the world pursuing graduate or postdoctoral study in the United States. Awards range from $20,000-$50,000.",
        "deadline_offset": 40,
        "application_link": "https://www.aauw.org/programs/fellowships-grants/"
    },
    {
        "title": "Commonwealth Scholarship",
        "provider": "Commonwealth Scholarship Commission",
        "country": "United Kingdom",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to Commonwealth citizens who are permanently resident in a developing Commonwealth country. Must have a first degree with upper second class honors.",
        "description": "Commonwealth Scholarships support outstanding graduates from developing Commonwealth countries to study at UK universities. Fully funded including tuition, living allowance, and travel.",
        "deadline_offset": 80,
        "application_link": "https://cscuk.fcdo.gov.uk/"
    },
    {
        "title": "Rotary Peace Fellowship",
        "provider": "Rotary Foundation",
        "country": "Multiple",
        "degree_level": "Master's, Certificate",
        "eligibility": "Open to professionals with work experience in peace and development. Must have a bachelor's degree and proficiency in English.",
        "description": "Rotary Peace Fellowships fund master's degrees or professional certificates in peace and conflict resolution at leading universities worldwide. Includes tuition, living expenses, and travel.",
        "deadline_offset": 65,
        "application_link": "https://www.rotary.org/en/our-programs/peace-fellowships"
    },
    {
        "title": "Schwarzman Scholars Program",
        "provider": "Schwarzman Scholars",
        "country": "China",
        "degree_level": "Master's",
        "eligibility": "Open to applicants aged 18-29 from all countries. Must have a bachelor's degree and demonstrate leadership, academic excellence, and interest in China.",
        "description": "Schwarzman Scholars is a fully funded one-year master's program in global affairs at Tsinghua University in Beijing. Includes tuition, room and board, travel, and a stipend.",
        "deadline_offset": 35,
        "application_link": "https://www.schwarzmanscholars.org/"
    },
    {
        "title": "Mastercard Foundation Scholars Program",
        "provider": "Mastercard Foundation",
        "country": "Multiple",
        "degree_level": "Bachelor's, Master's",
        "eligibility": "Open to academically talented but economically disadvantaged students from Sub-Saharan Africa. Must demonstrate leadership potential and commitment to giving back.",
        "description": "The Mastercard Foundation Scholars Program provides comprehensive scholarships to African students at partner universities worldwide. Covers full tuition, living expenses, mentorship, and leadership development.",
        "deadline_offset": 95,
        "application_link": "https://mastercardfdn.org/all/scholars/"
    },
    {
        "title": "Swedish Institute Scholarships for Global Professionals",
        "provider": "Swedish Institute",
        "country": "Sweden",
        "degree_level": "Master's",
        "eligibility": "Open to professionals from selected countries with at least 3,000 hours of work experience. Must have strong academic background and leadership experience.",
        "description": "SI Scholarships for Global Professionals fully fund master's programs in Sweden. Covers tuition, living expenses of SEK 12,000/month, travel grant, and insurance.",
        "deadline_offset": 105,
        "application_link": "https://si.se/en/apply/scholarships/"
    },
    {
        "title": "Yenching Academy of Peking University",
        "provider": "Peking University",
        "country": "China",
        "degree_level": "Master's",
        "eligibility": "Open to recent graduates from all countries with a bachelor's degree. Strong academic record and interest in China studies required.",
        "description": "Yenching Academy offers a fully funded one-year master's program in Chinese Studies at Peking University. Includes tuition, accommodation, travel, and living stipend.",
        "deadline_offset": 45,
        "application_link": "https://yenchingacademy.pku.edu.cn/"
    },
    {
        "title": "Orange Knowledge Programme",
        "provider": "Dutch Government",
        "country": "Netherlands",
        "degree_level": "Master's, Short Courses",
        "eligibility": "Open to professionals from 51 eligible countries with at least 2 years of work experience. Must have a bachelor's degree and employer endorsement.",
        "description": "The OKP funds master's degrees and short courses at Dutch universities for professionals from developing countries. Covers tuition, travel, living costs, and insurance.",
        "deadline_offset": 115,
        "application_link": "https://www.studyinholland.nl/finances"
    },
    {
        "title": "AFS Global STEM Scholars Program",
        "provider": "AFS Intercultural Programs",
        "country": "Multiple",
        "degree_level": "High School, Pre-University",
        "eligibility": "Open to students aged 15-18.5 from around the world with strong academic performance and interest in STEM and sustainability.",
        "description": "AFS Global STEM Scholars provides full scholarships for intercultural exchange programs focused on STEM and sustainability. Includes program fees, travel, and living expenses.",
        "deadline_offset": 25,
        "application_link": "https://afs.org/global-stem/"
    },
    {
        "title": "Clarendon Fund Scholarships at Oxford",
        "provider": "University of Oxford",
        "country": "United Kingdom",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to all graduate applicants to the University of Oxford regardless of nationality. Academic excellence is the primary criterion.",
        "description": "Clarendon Scholarships cover full tuition and college fees plus a generous living stipend for graduate study at Oxford. Over 1,000 Clarendon Scholars currently studying at Oxford.",
        "deadline_offset": 40,
        "application_link": "https://www.ox.ac.uk/admissions/graduate/fees-and-funding"
    },
    {
        "title": "Holland Scholarship",
        "provider": "Dutch Ministry of Education",
        "country": "Netherlands",
        "degree_level": "Bachelor's, Master's",
        "eligibility": "Open to students from outside the European Economic Area. Must be applying to a participating Dutch university for the first time.",
        "description": "The Holland Scholarship provides a one-time award of €5,000 in the first year of study at a Dutch university. Covers part of tuition or living expenses.",
        "deadline_offset": 55,
        "application_link": "https://www.studyinholland.nl/finances"
    },
    {
        "title": "Eiffel Excellence Scholarship Program",
        "provider": "French Ministry for Europe and Foreign Affairs",
        "country": "France",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to international students from developing and emerging countries. Must be under 30 for master's and under 35 for PhD programs.",
        "description": "Eiffel Scholarships support top international students in engineering, economics, law, and political science programs at French universities. Includes monthly allowance, travel, and insurance.",
        "deadline_offset": 70,
        "application_link": "https://www.campusfrance.org/en/the-eiffel-scholarship-program"
    },
    {
        "title": "Banting Postdoctoral Fellowship",
        "provider": "Canadian Government",
        "country": "Canada",
        "degree_level": "Postdoctoral",
        "eligibility": "Open to Canadian and international researchers who have completed a PhD within the last 3 years. Must have a research proposal accepted by a Canadian institution.",
        "description": "Banting Fellowships provide $70,000 per year for 2 years to postdoctoral researchers at Canadian universities. Supports the most promising researchers in health, natural sciences, and social sciences.",
        "deadline_offset": 60,
        "application_link": "https://banting.fellowships-bourses.gc.ca/"
    },
    {
        "title": "Weidenfeld-Hoffmann Scholarships at Oxford",
        "provider": "University of Oxford",
        "country": "United Kingdom",
        "degree_level": "Master's",
        "eligibility": "Open to students from developing and emerging economies. Must demonstrate academic excellence and commitment to public service in home country.",
        "description": "Weidenfeld-Hoffmann Scholarships provide full funding for graduate study at Oxford, including tuition and living costs. Focus on building leadership capacity in developing countries.",
        "deadline_offset": 50,
        "application_link": "https://www.weidenfeld-hoffmann-scholarship.org/"
    },
    {
        "title": "Korean Government Scholarship Program (KGSP)",
        "provider": "Korean Government",
        "country": "South Korea",
        "degree_level": "Bachelor's, Master's, PhD",
        "eligibility": "Open to citizens of countries with diplomatic relations with South Korea. Must be under 25 for undergraduate and under 40 for graduate programs.",
        "description": "KGSP provides full funding for international students to study at top Korean universities. Covers tuition, living allowance, airfare, language training, and medical insurance.",
        "deadline_offset": 80,
        "application_link": "https://www.niied.go.kr/"
    },
    {
        "title": "ADB-Japan Scholarship Program",
        "provider": "Asian Development Bank",
        "country": "Multiple (Asia-Pacific)",
        "degree_level": "Master's",
        "eligibility": "Open to nationals of ADB borrowing member countries. Must have a bachelor's degree and at least 2 years of professional work experience.",
        "description": "The ADB-JSP provides full scholarships for graduate study in economics, management, science, and technology at participating universities in the Asia-Pacific region.",
        "deadline_offset": 90,
        "application_link": "https://www.adb.org/work-with-us/careers/japan-scholarship-program"
    },
    {
        "title": "IMU Breakout Graduate Fellowship",
        "provider": "International Mathematical Union",
        "country": "Multiple",
        "degree_level": "PhD",
        "eligibility": "Open to outstanding students from developing countries who have been admitted to a PhD program in mathematics. Must demonstrate exceptional mathematical talent.",
        "description": "The IMU Breakout Graduate Fellowship supports PhD studies in mathematics for students from developing countries. Covers living expenses and research costs for up to 4 years.",
        "deadline_offset": 65,
        "application_link": "https://www.mathunion.org/imu-awards/breakout-graduate-fellowship"
    },
    {
        "title": "Global Korea Scholarship for Graduate Students",
        "provider": "Korean Government",
        "country": "South Korea",
        "degree_level": "Master's, PhD",
        "eligibility": "Open to international students from countries with diplomatic ties to Korea. Under 40, bachelor's degree for master's, master's for PhD. GPA 3.0+ preferred.",
        "description": "Global Korea Scholarship provides full tuition, monthly allowance of 1,000,000 KRW, airfare, Korean language training and medical insurance for graduate study at Korean universities.",
        "deadline_offset": 85,
        "application_link": "https://www.studyinkorea.go.kr/"
    },
]


def seed_scholarships():
    count = 0
    now = datetime.utcnow().date()

    for data in SCHOLARSHIPS:
        offset = data.pop("deadline_offset", 90)
        data["deadline"] = now + timedelta(days=offset)

        existing = Scholarship.query.filter_by(title=data["title"]).first()
        if existing:
            continue

        s = Scholarship(**data)
        db.session.add(s)
        count += 1

    db.session.commit()
    return count
